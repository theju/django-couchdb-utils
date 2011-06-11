from couchdb.ext.django.schema import *

class CacheRow(Document):
    key      = StringProperty()
    value    = StringProperty()
    expires  = DateTimeProperty()

    class Meta:
        app_label = "django_couchdb_utils_cache"

    @classmethod
    def get_row(cls, key):
        dbname = cls.get_db().dbname
        r = cls.view('%s/cache_by_key' % dbname
                     key=key, include_docs=True)
        return r.first() if r else None

    def _get_id(self):
        return self.key
    id = property(_get_id)
