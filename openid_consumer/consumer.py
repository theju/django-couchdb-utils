import couchdb, datetime
from django.conf import settings
from openid.consumer import consumer
from django_openid.consumer import signed
from openid_consumer.models import server_uri, DB_PREFIX
from django_openid.auth import AuthConsumer as DjangoOpenidAuthConsumer
# I know this long naming sucks! But couldn't think of anything better...
from django_openid.consumer import Consumer as DjangoOpenidConsumer, \
                                   LoginConsumer as DjangoOpenidLoginConsumer, \
                                   SessionConsumer as DjangoOpenidSessionConsumer, \
                                   CookieConsumer as DjangoOpenidCookieConsumer
from openid_consumer.models import DjangoCouchDBOpenIDStore, get_or_create, get_values

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
    def __init__(self):
        auth_db_prefix = getattr(settings, "COUCHDB_AUTH_PREFIX", "")
        self.auth_db = get_or_create(server_uri, "%s%s" %(auth_db_prefix, "auth"))
        super(AuthConsumer, self).__init__()

    def user_can_login(self, request, user):
        "Over-ride for things like user bans or account e-mail validation"
        return user.is_active

    def log_in_user(self, request, user):
        from auth import login
        user.backend = 'auth.backends.CouchDBAuthBackend'
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
            temp_db = get_or_create(server_uri, "%s%s" %(DB_PREFIX, "user_openid"))
            if not len(get_values(temp_db.view('openid_view/all', key = openid))):
                from openid_consumer.models import UserOpenidAssociation
                uoa = UserOpenidAssociation(user_id = request.user.id, 
                                            openid  = openid, 
                                            created = datetime.datetime.now())
                uoa.store(temp_db)
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
                        temp_db = get_or_create(server_uri, "%s%s" %(DB_PREFIX, "user_openid"))
                        from openid_consumer.models import UserOpenidAssociation
                        rows = get_values(temp_db.view('openid_view/all', key=todelete['openid']))
                        temp_db.delete(rows[0])
                        message = self.association_deleted_message % (
                            todelete['openid']
                        )
                except signed.BadSignature:
                    message = self.associate_tampering_message
        # We construct a button to delete each existing association
        openids = []
        temp_db = get_or_create(server_uri, "%s%s" %(DB_PREFIX, "user_openid"))
        for association in get_values(temp_db.view('openid_view/all')):
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
        from auth.models import User
        temp_db = get_or_create(server_uri, "%s%s" %(DB_PREFIX, "user_openid"))
        try:
            openid = get_values(temp_db.view('openid_view/all', key=identity_url))[0]
        except IndexError:
            return []
        return [User.load(self.auth_db, openid['user_id']),]

    def lookup_users_by_email(self, email):
        return get_values(self.auth_db.view('auth_email/all', key=email))

    def lookup_user_by_username(self, username):
        try:
            return get_values(self.auth_db.view('auth_id/all', key=username))
        except IndexError:
            return None

    def lookup_user_by_id(self, id):
        return lookup_by_username(id)
