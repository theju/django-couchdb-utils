from couchdb.ext.django.schema import *
from django.conf import settings

class CacheRow(Document):
    key      = StringProperty()
    value    = StringProperty()
    expires  = DateTimeProperty()

    @classmethod
    def get_row(cls, key):
        r = cls.view('%s/cache_by_key' % settings.COUCHDB_UTILS_CACHE_DB, 
                     key=key, include_docs=True)
        return r.first() if r else None

    def _get_id(self):
        return self.key
    id = property(_get_id)
