from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import get_hexdigest, check_password, UNUSABLE_PASSWORD
from couchdbkit.ext.django.schema import *


class User(Document):
    username      = StringProperty(required=True)
    first_name    = StringProperty(required=False)
    last_name     = StringProperty(required=False)
    email         = StringProperty(required=False)
    password      = StringProperty(required=True)
    is_staff      = BooleanProperty(default=False)
    is_active     = BooleanProperty(default=True)
    is_superuser  = BooleanProperty(default=False)
    last_login    = DateTimeProperty(required=False)
    date_joined   = DateTimeProperty(default=datetime.utcnow)

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return "<User: %s>" %self.username

    def is_anonymous(self):
        return False

    def save(self):
        if not self.check_username():
            raise Exception('This username is already in use')

        super(User, self).save()


    def check_username(self):
        u = User.get_user(self.username, is_active=None)
        if self._id is None or u is None:
            return True
        return u._id == self._id

    def _get_id(self):
        return self.username

    id = property(_get_id)

    def get_full_name(self):
        "Returns the first_name plus the last_name, with a space in between."
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

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
        return check_password(raw_password, self.password)

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

    @classmethod
    def get_user(cls, username, is_active=True):
        if is_active is None:
            param = dict(startkey=[username, False], endkey=[username, True])
        else:
            param = dict(key=[username, is_active])

        r = cls.view('django_couchdb_utils/users_by_username', include_docs=True, **param)
        return r.first() if r else None

    @classmethod
    def get_user_by_email(cls, email, is_active=True):
        if is_active is None:
            param = dict(startkey=[email, False], endkey=[email, True])
        else:
            param = dict(key=[email, is_active])

        r = cls.view('django_couchdb_utils/users_by_email', include_docs=True, **param)
        return r.first() if r else None

    @classmethod
    def all_users(cls):
        return cls.view('django_couchdb_utils/users_by_username', include_docs=True).iterator()


class CouchDBAuthBackend(object):
    # Create a User object if not exists.
    # Subclasses must override this attribute.
    create_unknown_user = False

    def authenticate(self, username=None, password=None):
        user = User.get_user(username)
        if user and check_password(password, user.password):
            return user
        if not user:
            if self.create_unknown_user:
                user = User(username)
                user.set_password(password)
                user.save()
                return user
            else:
                return None

    def get_user(self, username):
        user = User.get_user(username)
        if not user:
            raise KeyError
        return user


def migrate_users(
        get_user_data=lambda _: {},
        get_profile_data=lambda p: p.__dict__,
        progress_callback= lambda: None):

    from django.contrib.auth import models
    users = models.User.objects.all()
    ATTRIBS = ('username', 'first_name', 'last_name', 'email',
                'password', 'is_staff', 'is_active', 'is_superuser',
                'last_login', 'date_joined')

    total = users.count()
    for n, user in enumerate(users):

        data = user.__dict__

        try:
            profile = user.get_profile()
            data.update(get_profile_data(profile))
        except:
            pass

        data.update(get_user_data(user))

        # filter private variables
        data = dict( (k, v) for (k, v) in data.items() if not k.startswith('_') and k != 'user_id')

        new_user = User.get_user(data['username']) or User()

        for attrib, val in data.items():
            if attrib == 'id':
                continue

            setattr(new_user, attrib, val)

        new_user.save()

        progress_callback(n, total)
