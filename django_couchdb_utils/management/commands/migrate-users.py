from django.core.management.base import BaseCommand
from optparse import make_option
from django_couchdb_utils import auth

class Command(BaseCommand):

    def handle(self, *args, **options):
        auth.migrate_users()
