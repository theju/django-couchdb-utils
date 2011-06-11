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

    class Meta:
        app_label = "django_couchdb_utils_email"

    @classmethod
    def all_messages(cls):
        dbname = cls.get_db().dbname
        r = cls.view('%s/emails' % dbname, include_docs=True)
        return list(r)

    def __repr__(self):
        return 'EmailMessage (%s)' % self._id

