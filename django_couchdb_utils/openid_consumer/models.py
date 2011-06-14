from django.conf import settings
from couchdbkit.ext.django.schema import *
import time, base64, openid.store, urlparse
from django_openid.models import DjangoOpenIDStore
from django.utils.hashcompat import md5_constructor
from openid.association import Association as OIDAssociation
from couchdbkit.exceptions import ResourceNotFound

class UserOpenidAssociation(Document):
    user_id = StringProperty()
    openid  = StringProperty()
    created = DateTimeProperty()

    class Meta:
        app_label = "django_couchdb_utils_openid_consumer"

class Nonce(Document):
    server_url = StringProperty()
    timestamp  = IntegerProperty()
    salt       = StringProperty()

    class Meta:
        app_label = "django_couchdb_utils_openid_consumer"

class Association(Document):
    server_url = StringProperty()
    handle     = StringProperty()
    secret     = StringProperty() # Stored base64 encoded
    issued     = IntegerProperty()
    lifetime   = IntegerProperty()
    assoc_type = StringProperty()

    class Meta:
        app_label = "django_couchdb_utils_openid_consumer"

class DjangoCouchDBOpenIDStore(DjangoOpenIDStore):
    def __init__(self):
        # This constructor argument is specific only to
        # the couchdb store. It accepts a couchdb db 
        # instance
        self.nonce_db = Nonce.get_db()
        self.assoc_db = Association.get_db()
        self.user_openid_db = UserOpenidAssociation.get_db()

    def storeAssociation(self, server_url, association):
        assoc = Association(
            server_url = server_url,
            handle = association.handle,
            secret = base64.encodestring(association.secret),
            issued = association.issued,
            lifetime = association.issued,
            assoc_type = association.assoc_type
        )
        assoc.store()

    def getAssociation(self, server_url, handle=None):
        assocs = []
        if handle is not None:
            assocs = self.assoc_db.view('url_handle_view/all', key=[server_url, handle])
        else:
            assocs = self.assoc_db.view('url_view/all', key=server_url)
        assocs = assocs.iterator()
        associations = []
        try:
            for assoc in assocs:
                association = OIDAssociation(
                    assoc['handle'], base64.decodestring(assoc['secret']), assoc['issued'],
                    assoc['lifetime'], assoc['assoc_type']
                    )
                if association.getExpiresIn() == 0:
                    self.removeAssociation(server_url, assoc.handle)
                else:
                    associations.append((association.issued, association))
        except ResourceNotFound:
            pass
        if not associations:
            return None
        return associations[-1][1]

    def removeAssociation(self, server_url, handle):
        assocs = self.assoc_db.view('url_handle_view/all', key=[server_url, handle])
        assocs_exist = len(assocs) > 0
        for assoc in assocs:
            self.assoc_db.delete(assoc)
        return assocs_exist

    def useNonce(self, server_url, timestamp, salt):
        # Has nonce expired?
        if abs(timestamp - time.time()) > openid.store.nonce.SKEW:
            return False
        try:
            nonce = self.nonce_db.view('url_timestamp_salt_view/all', 
                                       key=[server_url, timestamp, salt]).first()
        except IndexError:
            nonce = Nonce(
                server_url = server_url,
                timestamp = timestamp,
                salt = salt
            )
            nonce.store()
            return True
        self.nonce_db.delete(nonce)
        return False

    def cleanupNonce(self):
        max_key_val = time.time() - openid.store.nonce.SKEW
        nonces = self.nonce_db.view('timestamp_view/all', endkey=max_key_val)
        for nonce in nonces:
            self.nonce_db.delete(nonce)

    def cleaupAssociations(self):
        assocs = self.assoc_db.view('issued_lifetime_view/all', endkey=time.time())
        for assoc in assocs:
            self.assoc_db.delete(assoc)
