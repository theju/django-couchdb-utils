from couchdbkit.ext.django.schema import *

from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


DEFAULT_WRAPPED_BACKEND='django.core.mail.backends.smtp.EmailBackend'
COPY_PROPERTIES=('subject', 'body', 'from_email', 'to', 'cc', 'bcc', 'headers')


class EmailMessage(Document):
    """
    A couchdbkit Document to store emails, uses the same properties as
    django.core.mail.EmailMessage
    """

    subject     = StringProperty()
    body        = StringProperty()
    from_email  = StringProperty(default=settings.DEFAULT_FROM_EMAIL)
    to          = StringListProperty()
    cc          = StringListProperty()
    bcc         = StringListProperty()
#   attachments = blobs/attachments ?
    headers     = DictProperty()

    @classmethod
    def all_messages(cls):
        r = cls.view('django_couchdb_utils/emails', include_docs=True)
        return list(r)

    def __repr__(self):
        return 'EmailMessage (%s)' % self._id


class CouchDBEmailBackend(BaseEmailBackend):
    """
    A Django email backend that wraps caching in a CouchDB around another
    backend. The backend tries to send emails, if this fails it stores the
    message in a CouchDB database for a later retry.
    """

    def open(self):
        wrapped_backend = getattr(settings, 'COUCHDB_EMAIL_BACKEND', DEFAULT_WRAPPED_BACKEND)
        self.backend = mail.get_connection(backend=wrapped_backend)
        self.backend.open()

    def close(self):
        self.backend.close()

    def send_messages(self, email_messages):
        for email in email_messages:
            try:
                self.backend.send_messages([msg])
            except:
                self._store_email(email)


    def send_cached_emails(self):
        self.open()

        success, failed = 0, 0
        docs = EmailMessage.all_messages()
        for doc in docs:
            email = self._doc_to_email(doc)
            try:
                self.backend.send_messages([email])
                doc.delete()
                success += 1
            except:
                failed += 1

        self.close()
        return success, failed


    def _store_email(self, email):
        msg = self._email_to_doc(email)
        msg.save()

    def _email_to_doc(self, message):
        msg = EmailMessage()
        for p in COPY_PROPERTIES:
            setattr(msg, p, getattr(message, p, None))
        return msg

    def _doc_to_email(self, message):
        msg = mail.EmailMessage()
        for p in COPY_PROPERTIES:
            setattr(msg, p, getattr(message, p, None))
        return msg
