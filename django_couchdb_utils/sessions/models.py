from couchdbkit.ext.django.schema import *
from couchdbkit.exceptions import ResourceNotFound

class Session(Document):
    session_key  = StringProperty()
    session_data = StringProperty()
    expire_date  = StringProperty()

    class Meta:
        app_label = "django_couchdb_utils_sessions"

    @classmethod
    def get_session(cls, session_key):
        r = cls.view('%s/sessions_by_key' % cls._meta.app_label, key=session_key, include_docs=True)
        try:
            return r.first()
        except ResourceNotFound:
            return None
