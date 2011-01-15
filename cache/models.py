from couchdb.ext.django.schema import *

class CacheRow(Document):
    key      = StringProperty()
    value    = StringProperty()
    expires  = DateTimeProperty()

    @classmethod
    def get_row(cls, key):
        r = cls.view('cache/by_key', key=key, include_docs=True)
        return r.first() if r else None

    def _get_id(self):
        return self.key

    id = property(_get_id)
