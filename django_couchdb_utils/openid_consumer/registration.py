from django_couchdb_utils.auth.models import User
from datetime import datetime
from django.http import Http404
from django_openid import signed
from django.conf import settings
from .consumer import AuthConsumer
from .forms import RegistrationFormPasswordConfirm
from .models import UserOpenidAssociation
from django_openid.registration import RegistrationConsumer as DjangoOpenIDRegistrationConsumer
from couchdbkit.exceptions import ResourceNotFound

class RegistrationConsumer(AuthConsumer, DjangoOpenIDRegistrationConsumer):
    RegistrationForm   = RegistrationFormPasswordConfirm

    def user_is_unconfirmed(self, user):
        count = 0
        try:
            count = User.view('%s/users_by_username' % User._meta.app_label, 
                              key=user.username, include_docs=True).count()
        except ResourceNotFound:
            return False
        if count:
            return True
        return False

    def mark_user_confirmed(self, user):
        user.is_active = True
        return user.store()

    def mark_user_unconfirmed(self, user):
        user.is_active = False
        return user.store()

    def create_user(self, request, data, openid=None):
        user = User(
            username = data['username'],
            first_name = data.get('first_name', ''),
            last_name = data.get('last_name', ''),
            email = data.get('email', ''),
        )
        # Set OpenID, if one has been associated
        if openid:
            uoa = UserOpenidAssociation(user_id = user.username, 
                                        openid  = openid, 
                                        created = datetime.now())
            uoa.store()            
        # Set password, if one has been specified
        password = data.get('password')
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.store()
        return user

    def suggest_nickname(self, nickname):
        "Return a suggested nickname that has not yet been taken"
        if not nickname:
            return ''
        original_nickname = nickname
        suffix = None
        username_exists = True
        while username_exists:
            try:
                username_exists = User.view('%s/users_by_username' % User._meta.app_label, 
                                            key=nickname, include_docs=True).count()
            except ResourceNotFound:
                username_exists = False
            if not username_exists:
                break
            if suffix is None:
                suffix = 1
            else:
                suffix += 1
            nickname = original_nickname + str(suffix)
        return nickname

    def generate_confirm_code(self, user):
        return signed.sign(str(user.id), key = (
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
                u.store()
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
            try:
                user = User.view('%s/users_by_username' % User._meta.app_label, 
                                 key=user.username, include_docs=True).first()
            except ResourceNotFound:
                user = None
            if user:
                self.mark_user_confirmed(user)
                self.log_in_user(request, user)
            return self.on_registration_complete(request)
        else:
            return self.show_error(request, self.c_already_confirmed_message)

    do_c.urlregex = '^c/([^/]+)/$'
