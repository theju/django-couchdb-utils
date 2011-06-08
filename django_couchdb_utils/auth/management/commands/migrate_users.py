from django.core.management.base import BaseCommand
from optparse import make_option
from django.contrib.auth.models import User as Dj_User
from django_couchdb_utils.auth.models import User

def migrate_users(
        get_user_data=lambda _: {},
        get_profile_data=lambda p: p.__dict__,
        progress_callback= lambda: None):

    users = Dj_User.objects.all()
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

class Command(BaseCommand):
    """Migrate django db backed users to the couchdb backed database"""

    def handle(self, *args, **options):
        migrate_users()
