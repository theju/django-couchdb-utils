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
            assocs = Association.view('%s/url_handle_view' % Association._meta.app_label, 
                                      key=[server_url, handle], include_docs=True).all()
        else:
            assocs = Association.view('%s/url_view' % Association._meta.app_label, 
                                        key=server_url, include_docs=True).all()
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
        try:
            assocs = Association.view('%s/url_handle_view' % Association._meta.app_label, 
                                      key=[server_url, handle], include_docs=True).all()
        except ResourceNotFound:
            assocs = []
        for assoc in assocs:
            assoc.delete()
        return len(assocs)

    def useNonce(self, server_url, timestamp, salt):
        # Has nonce expired?
        if abs(timestamp - time.time()) > openid.store.nonce.SKEW:
            return False
        nonce = Nonce.view('%s/url_timestamp_salt_view' % Nonce._meta.app_label, 
                           key=[server_url, timestamp, salt], include_docs=True).first()
        if not nonce:
            nonce = Nonce(
                server_url = server_url,
                timestamp = timestamp,
                salt = salt
            )
            nonce.store()
            return True
        if nonce:
            nonce.delete()
        return False

    def cleanupNonce(self):
        max_key_val = time.time() - openid.store.nonce.SKEW
        nonces = Nonce.view('%s/timestamp_view' % Nonce._meta.app_label, 
                            endkey=max_key_val, include_docs=True)
        for nonce in nonces:
            nonce.delete()

    def cleaupAssociations(self):
        assocs = Association.view('%s/issued_lifetime_view' % Association._meta.app_label, 
                                   endkey=time.time(), include_docs=True)
        for assoc in assocs:
            assoc.delete()
