from couchdbkit.ext.django.schema import *

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

