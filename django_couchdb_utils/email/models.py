from couchdbkit.ext.django.schema import *
from django.conf import settings

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
        r = cls.view('%s/emails' % settings.COUCHDB_UTILS_EMAIL_DB, include_docs=True)
        return list(r)

    def __repr__(self):
        return 'EmailMessage (%s)' % self._id

