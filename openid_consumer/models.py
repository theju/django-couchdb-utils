from couchdb.schema import *
from couchdb.schema import View
from django.conf import settings
from couchdb import Server, Database
import time, base64, openid.store, urlparse
from couchdb.client import PreconditionFailed
from django_openid.models import DjangoOpenIDStore
from django.utils.hashcompat import md5_constructor
from openid.association import Association as OIDAssociation

DEFAULT_COUCHDB_HOST = "http://127.0.0.1:5984"
server_uri           = getattr(settings, 'COUCHDB_HOST', DEFAULT_COUCHDB_HOST)
DB_PREFIX            = getattr(settings, 'COUCHDB_OPENID_PREFIX', '')
openid_db_uri        = getattr(settings, 'COUCHDB_OPENID_DB', '%s%s' %(DB_PREFIX, 'openid'))

def get_or_create(server_uri, db_name):
    server = Server(server_uri)
    try:
        db = server.create(db_name)
    except PreconditionFailed, e:
        if not e.message[0] == 'file_exists':
            raise e
        # Database seems to exist. Let's just use it
        db = Database(urlparse.urljoin(server_uri, db_name))
    return db

def get_values(db_view_result):
    return [i['value'] for i in db_view_result.rows]


def couch_auth_models_available():
    auth_backends = getattr(settings, 'AUTHENTICATION_BACKENDS', None)
    # Slightly hackish. Hopefully it will be refactored soon
    if auth_backends and [i for i in auth_backends if 'backends.CouchDBAuthBackend' in i]:
        return True

if couch_auth_models_available():
    from auth.models import User
    class UserOpenidAssociation(Document):
        user_id = TextField()
        openid  = TextField()
        created = DateTimeField()

        openid_view = View('openid_view',
                           '''function (doc) { emit(doc.openid, doc); }''',
                           name='all')

class Nonce(Document):
    server_url = TextField()
    timestamp  = IntegerField()
    salt       = TextField()

    timestamp_view          = View('timestamp_view', 
                                   '''function (doc) { emit(doc.timestamp, doc); }''', 
                                   name='all')
    url_timestamp_salt_view = View('url_timestamp_salt_view',
                                   '''function (doc) { emit([doc.server_url, doc.timestamp, doc.salt], doc); }''',
                                   name='all')

class Association(Document):
    server_url = TextField()
    handle     = TextField()
    secret     = TextField() # Stored base64 encoded
    issued     = IntegerField()
    lifetime   = IntegerField()
    assoc_type = TextField()

    url_handle_view      = View('url_handle_view', 
                                '''function (doc) { emit([doc.server_url, doc.handle], doc); }''',
                                name='all')
    url_view             = View('url_view',
                                '''function (doc) { emit(doc.server_url, doc); }''',
                                name='all')
    issued_lifetime_view = View('issued_lifetime_view',
                                '''function (doc) { emit(doc.issued+doc.lifetime, doc); } ''',
                                name='all')

class DjangoCouchDBOpenIDStore(DjangoOpenIDStore):
    def __init__(self):
        # This constructor argument is specific only to
        # the couchdb store. It accepts a couchdb db 
        # instance
        self.nonce_db = get_or_create(server_uri, "%s_nonce" %openid_db_uri)
        self.assoc_db = get_or_create(server_uri, "%s_assoc" %openid_db_uri)
        if couch_auth_models_available():
            self.user_openid_db = get_or_create(server_uri, "user_openid")
            UserOpenidAssociation.openid_view.sync(self.user_openid_db)
        Nonce.timestamp_view.sync(self.nonce_db)
        Nonce.url_timestamp_salt_view.sync(self.nonce_db)
        Association.url_handle_view.sync(self.assoc_db)
        Association.url_view.sync(self.assoc_db)
        Association.issued_lifetime_view.sync(self.assoc_db)

    def storeAssociation(self, server_url, association):
        assoc = Association(
            server_url = server_url,
            handle = association.handle,
            secret = base64.encodestring(association.secret),
            issued = association.issued,
            lifetime = association.issued,
            assoc_type = association.assoc_type
        )
        assoc.store(self.assoc_db)

    def getAssociation(self, server_url, handle=None):
        assocs = []
        if handle is not None:
            assocs = get_values(self.assoc_db.view('url_handle_view/all', key=[server_url, handle]))
        else:
            assocs = get_values(self.assoc_db.view('url_view/all', key=server_url))
        if not assocs:
            return None
        associations = []
        for assoc in assocs:
            association = OIDAssociation(
                assoc['handle'], base64.decodestring(assoc['secret']), assoc['issued'],
                assoc['lifetime'], assoc['assoc_type']
            )
            if association.getExpiresIn() == 0:
               self.removeAssociation(server_url, assoc.handle)
            else:
                associations.append((association.issued, association))
        if not associations:
            return None
        return associations[-1][1]

    def removeAssociation(self, server_url, handle):
        assocs = get_values(self.assoc_db.view('url_handle_view/all', key=[server_url, handle]))
        assocs_exist = len(assocs) > 0
        for assoc in assocs:
            self.assoc_db.delete(assoc)
        return assocs_exist

    def useNonce(self, server_url, timestamp, salt):
        # Has nonce expired?
        if abs(timestamp - time.time()) > openid.store.nonce.SKEW:
            return False
        try:
            nonce = get_values(self.nonce_db.view('url_timestamp_salt_view/all', 
                                                  key=[server_url, timestamp, salt]))[0]
        except IndexError:
            nonce = Nonce(
                server_url = server_url,
                timestamp = timestamp,
                salt = salt
            )
            nonce.store(self.nonce_db)
            return True
        self.nonce_db.delete(nonce)
        return False

    def cleanupNonce(self):
        max_key_val = time.time() - openid.store.nonce.SKEW
        nonces = get_values(self.nonce_db.view('timestamp_view/all', endkey=max_key_val))
        for nonce in nonces:
            self.nonce_db.delete(nonce)

    def cleaupAssociations(self):
        assocs = get_values(self.assoc_db.view('issued_lifetime_view/all', endkey=time.time()))
        for assoc in assocs:
            self.assoc_db.delete(assoc)
