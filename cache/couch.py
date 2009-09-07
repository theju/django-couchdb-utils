"CouchDB cache backend"

from time import strptime
from models import CacheRow
from django.conf import settings
from datetime import datetime, timedelta
from django.utils.encoding import smart_unicode, smart_str
from django.core.cache.backends.base import BaseCache, InvalidCacheBackendError

try:
    import couchdb
except ImportError:
    raise InvalidCacheBackendError("CouchDB cache backend requires the 'couchdb-python' library")

class CacheClass(BaseCache):
    def __init__(self, server, params):
        BaseCache.__init__(self, params)
        server = couchdb.Server(server or getattr(settings, 'COUCHDB_HOST'))
        try:
            self._cache = server['cache']
        except couchdb.ResourceNotFound:
            self._cache = server.create('cache')            
            CacheRow.get_keys.sync(self._cache)

    def add(self, key, value, timeout=0):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        timeout_secs = timeout or self.default_timeout
        expire_time = datetime.now() + timedelta(seconds = timeout_secs)
        return CacheRow(id=key, value=value, expires = expire_time).store(self._cache)

    def get(self, key, default=None):
        val = CacheRow.load(self._cache, smart_str(key))
        if not val:
            return default
        if val['expires'] > datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'):
            if isinstance(val, basestring):
                return smart_unicode(val)
            else:
                return val

    def set(self, key, value, timeout=0):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        expire_time = datetime.now() + timedelta(seconds=timeout)
        doc = CacheRow.load(self._cache, smart_str(key))
        if doc:
            doc._data.update({'value': value, 'expires': expire_time.strftime('%Y-%m-%dT%H:%M:%SZ')})
            doc.store(self._cache)
        else:
            CacheRow(id=key, value=value, expires=expire_time).store(self._cache)

    def delete(self, key):
        doc = CacheRow.load(self._cache, key)
        if doc:
            self._cache.delete(doc)

    def get_many(self, keys):
        return CacheRow.get_keys(self._cache, keys = map(smart_str,keys))

    def incr(self, key, delta=1):
        if key not in self:
            raise ValueError, "Key '%s' not found" % key
        new_value = self.get(key)['value'] + delta
        self.set(key, new_value)
        return new_value
