from django.conf import settings
from .models import User

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
