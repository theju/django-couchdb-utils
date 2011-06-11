from couchdbkit.ext.django.schema import *
from django.conf import settings

class Session(Document):
    session_key  = StringProperty()
    session_data = StringProperty()
    expire_date  = StringProperty()

    @classmethod
    def get_session(cls, session_key):
        r = cls.view('%s/sessions_by_key' % settings.COUCHDB_UTILS_SESSIONS_DB, 
                     key=session_key, include_docs=True)
        return r.first() if r else None
