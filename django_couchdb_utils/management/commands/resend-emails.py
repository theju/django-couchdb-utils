from django.core.management.base import BaseCommand
from optparse import make_option
from django.core import mail

class Command(BaseCommand):
    """
    Resends emails that have been cached by the CouchDB Email backend because
    sending failed
    """

    def handle(self, *args, **options):
        backend = mail.get_connection()
        success, failed = backend.send_cached_emails()
        print 'Mails sent: %d, failed: %d' % (success, failed)
