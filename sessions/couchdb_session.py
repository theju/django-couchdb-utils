from couchdb import Server
from django.conf import settings
from sessions.models import Session
from couchdb.client import ResourceNotFound
from django.core.exceptions import SuspiciousOperation
from django.contrib.sessions.backends.base import SessionBase, CreateError

DB_PREFIX = getattr(settings, "COUCHDB_SESSION_PREFIX", "")

class SessionStore(SessionBase):
    def __init__(self, session_key=None):
        server = Server(getattr(settings,'COUCHDB_HOST'))
        try:
            self.db = server["%s%s" %(DB_PREFIX, 'session')]
        except ResourceNotFound:
            # Create the db and views.
            self.db = server.create("%s%s" %(DB_PREFIX, 'session'))
        super(SessionStore, self).__init__(session_key)

    def create(self):
        while True:
            self.session_key = self._get_new_session_key()
            self.modified = True
            self._session_cache = {}
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            return None
    
    def load(self):
        session = Session.load(self.db, self.session_key)
        if not session:
            self.create()
            return {}
        try:
            return self.decode(session['session_data'])
        except SuspiciousOperation:
            return {}
        
    def save(self, must_create=False):
        session = Session.load(self.db, self.session_key)
        if must_create and session:
            raise CreateError
        if must_create:
            session_dict = {
                'id': self.session_key,
                'session_data': self.encode(self._get_session(no_load=must_create)),
                'expire_date': self.get_expiry_date().strftime('%Y-%m-%dT%H:%M:%SZ')
                }
            session = Session(**session_dict)
        else:
            if not session:
                return None
            session['session_data'] = self.encode(self._get_session(no_load=must_create))
            session['expire_date']  = self.get_expiry_date().strftime('%Y-%m-%dT%H:%M:%SZ')
        session.store(self.db)
            
    def exists(self, session_key):
        session = Session.load(self.db, session_key)
        if session is None:
            return False
        return True
        
    def delete(self, session_key=None):
        if not session_key:
            if not self._session_key:
                return None
            session_key = self._session_key
        session = Session.load(self.db, session_key)
        if not session:
            return None
        self.db.delete(session)
