from couchdb import Server
from auth.models import User
from django.conf import settings
from couchdb.client import ResourceNotFound
from django.contrib.auth.models import get_hexdigest, check_password

class CouchDBAuthBackend(object):
    # Create a User object if not exists.
    # Subclasses must override this attribute.
    create_unknown_user = False

    def __init__(self):
        server  = Server(getattr(settings, 'COUCHDB_HOST'))
        self.db = server['auth']
        try:
            self.db.info()
        except ResourceNotFound:
            server.create('auth')

    def authenticate(self, username=None, password=None):
        user = User.load(self.db, username)
        if user and check_password(password, user.password):
            return user
        if not user:
            if self.create_unknown_user:
                user_dict = {
                             'id'        : username, 
                            }
                user = User(**user_dict)
                user.set_password(password)
                user.save()
                return user
            else:
                return None

    def get_user(self, user_id):
        user = User.load(self.db, user_id)
        if not user:
            raise KeyError
        return user
