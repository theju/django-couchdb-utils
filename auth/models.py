from auth import get_or_create
from couchdb import Server
from couchdb.schema import *
from couchdb.schema import View
from django.conf import settings
from couchdb.client import ResourceNotFound
from django.contrib.auth.models import get_hexdigest, check_password, UNUSABLE_PASSWORD

class User(Document):
    # username == id
    first_name    = TextField()
    last_name     = TextField()
    email         = TextField()
    password      = TextField()
    is_staff      = BooleanField(default=False)
    is_active     = BooleanField(default=True)
    is_superuser  = BooleanField(default=False)
    last_login    = DateTimeField()
    date_joined   = DateTimeField()

    id_view        = View('auth_id', 
                          '''function (doc) { emit(doc.id, doc); }''',
                          name='all')
    email_view     = View('auth_email', 
                          '''function (doc) { emit(doc.email, doc); }''',
                          name='all')
    is_active_view = View('auth_is_active', 
                          '''function (doc) { emit(doc.is_active, doc); }''',
                          name='all')

    def __init__(self, id=None, **values):
        super(User, self).__init__(id, **values)
        server_uri = getattr(settings, 'COUCHDB_HOST'))
        self.db = get_or_create(server_uri, "auth")
        self.set_password(self.password)

    def __unicode__(self):
        return self.id

    def __repr__(self):
        return "<User: %s>" %self.id

    def is_anonymous(self):
        return False

    def get_full_name(self):
        "Returns the first_name plus the last_name, with a space in between."
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def save(self):
        return self.store(self.db)

    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        user = self.load(self.db, self.id)
        if not user:
            return False
        return check_password(raw_password, user.password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        return self.password != UNUSABLE_PASSWORD

    def email_user(self, subject, message, from_email=None):
        "Sends an e-mail to this User."
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email])

    def get_and_delete_messages(self):
        # Todo: Implement messaging and groups.
        return None
