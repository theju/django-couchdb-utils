from datetime import datetime
from django.http import Http404
from django_openid import signed
from django.conf import settings
from openid_consumer.consumer import AuthConsumer
from openid_consumer.forms import RegistrationFormPasswordConfirm
from openid_consumer.models import server_uri, DB_PREFIX, get_values, get_or_create
from django_openid.registration import RegistrationConsumer as DjangoOpenIDRegistrationConsumer

class RegistrationConsumer(AuthConsumer, DjangoOpenIDRegistrationConsumer):
    RegistrationForm   = RegistrationFormPasswordConfirm

    def user_is_unconfirmed(self, user):
        return len(get_values(self.auth_db.view('auth_is_active/all', key=[user.id, False])))

    def mark_user_confirmed(self, user):
        self.auth_db.delete(user)

    def mark_user_unconfirmed(self, user):
        user.is_active = False
        user.store(self.auth_db)

    def create_user(self, request, data, openid=None):
        from auth.models import User
        user = User(
            id = data['username'],
            first_name = data.get('first_name', ''),
            last_name = data.get('last_name', ''),
            email = data.get('email', ''),
        )
        user.store(self.auth_db)
        # Set OpenID, if one has been associated
        if openid:
            from openid_consumer.models import UserOpenidAssociation
            temp_db = get_or_create(server_uri, "%s%s" %(DB_PREFIX, 'user_openid'))
            uoa = UserOpenidAssociation(user_id = user.id, 
                                        openid  = openid, 
                                        created = datetime.now())
            uoa.store(temp_db)            
        # Set password, if one has been specified
        password = data.get('password')
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.store(self.auth_db)
        return user

    def suggest_nickname(self, nickname):
        "Return a suggested nickname that has not yet been taken"
        if not nickname:
            return ''
        original_nickname = nickname
        suffix = None
        while len(self.auth_db.view('auth_id/all', key=nickname).rows):
            if suffix is None:
                suffix = 1
            else:
                suffix += 1
            nickname = original_nickname + str(suffix)
        return nickname

    def generate_confirm_code(self, user):
        return signed.sign(user.id, key = (
            self.confirm_link_secret or settings.SECRET_KEY
        ) + self.confirm_link_salt)

    def do_password(self, request):
        "Allow users to set a password on their account"
        if request.user.is_anonymous():
            return self.show_error(request, 'You need to log in first')
        ChangePasswordForm = self.get_change_password_form_class(request)
        if request.method == 'POST':
            form = ChangePasswordForm(request.user, data=request.POST)
            if form.is_valid():
                u = request.user
                u.set_password(form.cleaned_data['password'])
                u.store(self.auth_db)
                return self.show_password_has_been_set(request)
        else:
            form = ChangePasswordForm(request.user)
        return self.render(request, self.set_password_template, {
            'form': form,
            'action': request.path,
        })

    def do_c(self, request, token = ''):
        if not token:
            # TODO: show a form where they can paste in their token?
            raise Http404
        token = token.rstrip('/').encode('utf8')
        try:
            value = signed.unsign(token, key = (
                self.confirm_link_secret or settings.SECRET_KEY
            ) + self.confirm_link_salt)
        except signed.BadSignature:
            return self.show_message(
                request, self.invalid_token_message,
                self.invalid_token_message + ': ' + token
            )
        # Only line change compared with django-openid
        user_id = value
        user = self.lookup_user_by_id(user_id)
        if not user: # Maybe the user was deleted?
            return self.show_error(request, self.r_user_not_found_message)

        # Check user is NOT active but IS in the correct group
        if self.user_is_unconfirmed(user):
            # Confirm them
            user.is_active = True
            user.save()
            self.mark_user_confirmed(user)
            self.log_in_user(request, user)
            return self.on_registration_complete(request)
        else:
            return self.show_error(request, self.c_already_confirmed_message)

    do_c.urlregex = '^c/([^/]+)/$'
