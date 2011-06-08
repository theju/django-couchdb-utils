from couchdbkit.ext.django.schema import *

class Session(Document):
    session_key  = StringProperty()
    session_data = StringProperty()
    expire_date  = StringProperty()

    @classmethod
    def get_session(cls, session_key):
        r = cls.view('django_couchdb_utils/sessions_by_key', key=session_key, include_docs=True)
        return r.first() if r else None
