from couchdb.ext.django.schema import *
from couchdbkit.exceptions import ResourceNotFound

class CacheRow(Document):
    key      = StringProperty()
    value    = StringProperty()
    expires  = DateTimeProperty()

    class Meta:
        app_label = "django_couchdb_utils_cache"

    @classmethod
    def get_row(cls, key):
        r = cls.view('%s/cache_by_key' % cls._meta.app_label, key=key, include_docs=True)
        try:
            return r.first()
        except ResourceNotFound:
            return None

    def _get_id(self):
        return self.key
    id = property(_get_id)
