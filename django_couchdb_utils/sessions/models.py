from couchdbkit.ext.django.schema import *

class Session(Document):
    session_key  = StringProperty()
    session_data = StringProperty()
    expire_date  = StringProperty()

    class Meta:
        app_label = "django_couchdb_utils_sessions"

    @classmethod
    def get_session(cls, session_key):
        dbname = cls.get_db().dbname
        r = cls.view('%s/sessions_by_key' % dbname, key=session_key, include_docs=True)
        return r.first() if r else None
