import datetime
from django.conf import settings
from openid.consumer import consumer
from django_openid.consumer import signed
from django_openid.auth import AuthConsumer as DjangoOpenidAuthConsumer
# I know this long naming sucks! But couldn't think of anything better...
from django_openid.consumer import Consumer as DjangoOpenidConsumer, \
                                   LoginConsumer as DjangoOpenidLoginConsumer, \
                                   SessionConsumer as DjangoOpenidSessionConsumer, \
                                   CookieConsumer as DjangoOpenidCookieConsumer
from .models import DjangoCouchDBOpenIDStore, UserOpenidAssociation
from django_couchdb_utils.auth.models import User
from django.contrib.auth import login
from couchdbkit.exceptions import ResourceNotFound

class Consumer(DjangoOpenidConsumer):
    def get_consumer(self, request, session_store):
        return consumer.Consumer(session_store, DjangoCouchDBOpenIDStore())

class LoginConsumer(Consumer, DjangoOpenidLoginConsumer):
    pass

class SessionConsumer(LoginConsumer, DjangoOpenidSessionConsumer):
    pass

class CookieConsumer(LoginConsumer, DjangoOpenidCookieConsumer):
    pass

class AuthConsumer(SessionConsumer, DjangoOpenidAuthConsumer):
    def user_can_login(self, request, user):
        "Over-ride for things like user bans or account e-mail validation"
        return user.is_active

    def log_in_user(self, request, user):
        user.backend = 'django_couchdb_utils.auth.backends.CouchDBAuthBackend'
        login(request, user)

    def do_associate(self, request):
        if request.method == 'POST':
            try:
                openid = signed.loads(
                    request.POST.get('openid_token', ''),
                    extra_salt = self.associate_salt + str(request.user.id)
                )
            except signed.BadSignature:
                return self.show_error(request, self.csrf_failed_message)
            # Associate openid with their account, if it isn't already
            if not len(UserOpenidAssociation.view('%s/openid_view' % UserOpenidAssociation._meta.app_label, 
                                                  key = openid), include_docs=True):
                uoa = UserOpenidAssociation(user_id = request.user.id, 
                                            openid  = openid, 
                                            created = datetime.datetime.now())
                uoa["temp"] = True
                uoa.store()
            return self.show_associate_done(request, openid)

        return self.show_error(request, 'Should POST to here')

    def do_associations(self, request):
        "Interface for managing your account's associated OpenIDs"
        if not request.user.is_authenticated():
            return self.need_authenticated_user(request)
        message = None
        if request.method == 'POST':
            if 'todelete' in request.POST:
                # Something needs deleting; find out what
                try:
                    todelete = signed.loads(
                        request.POST['todelete'],
                        extra_salt = self.associate_delete_salt
                    )
                    if todelete['user_id'] != request.user.id:
                        message = self.associate_tampering_message
                    else:
                        # It matches! Delete the OpenID relationship
                        row = UserOpenidAssociation.view('%s/openid_view' % UserOpenidAssociation._meta.app_label, 
                                                         key=todelete['openid'], include_docs=True).first()
                        if row.temp == True:
                            row.delete()
                            message = self.association_deleted_message % (
                                todelete['openid']
                                )
                except signed.BadSignature:
                    message = self.associate_tampering_message
        # We construct a button to delete each existing association
        openids = []
        for association in UserOpenidAssociation.view('%s/openid_view' % UserOpenidAssociation._meta.app_label, 
                                                      include_docs=True):
            openids.append({
                'openid': association['openid'],
                'button': signed.dumps({
                    'user_id': request.user.id,
                    'association_id': association['_id'],
                    'openid': association['openid'],
                }, extra_salt = self.associate_delete_salt),
            })
        return self.render(request, self.associations_template, {
            'openids': openids,
            'user': request.user,
            'action': request.path,
            'message': message,
            'action_new': '../',
            'associate_next': self.sign_next(request.path),
        })


    def lookup_openid(self, request, identity_url):
        openid = UserOpenidAssociation.view('%s/openid_view' % UserOpenidAssociation._meta.app_label, 
                                            key=identity_url, include_docs=True).first()
        if openid:
            return User.view('%s/users_by_username' % User._meta.app_label, 
                             key=openid['user_id'], include_docs=True).all()

    def lookup_users_by_email(self, email):
        return User.view('%s/users_by_email' % User._meta.app_label, 
                         key=email, include_docs=True).first()

    def lookup_user_by_username(self, username):
        return User.view('%s/users_by_username' % User._meta.app_label, 
                         key=username, include_docs=True).first()

    def lookup_user_by_id(self, id):
        return self.lookup_user_by_username(id)
