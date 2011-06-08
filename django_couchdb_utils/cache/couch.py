from datetime import datetime, timedelta
from django.utils.encoding import smart_unicode, smart_str
from django.core.cache.backends.base import BaseCache, InvalidCacheBackendError

class CacheClass(BaseCache):

    def add(self, key, value, timeout=0):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        timeout_secs = timeout or self.default_timeout
        expire_time = datetime.now() + timedelta(seconds = timeout_secs)

        row = CacheRow()
        row.key = key
        row.value = value
        row.expires=expire_time
        row.save()
        return row

    def get(self, key, default=None):
        val = CacheRow.get_row(smart_str(key))
        if not val:
            return default
        if val.expires > datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'):
            if isinstance(val, basestring):
                return smart_unicode(val)
            else:
                return val

    def set(self, key, value, timeout=0):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        expire_time = datetime.now() + timedelta(seconds=timeout)
        doc = CacheRow.get_row(smart_str(key))
        if doc:
            doc._data.update({'value': value, 'expires': expire_time.strftime('%Y-%m-%dT%H:%M:%SZ')})
            doc.save()
        else:
            row = CacheRow()
            row.key = key
            row.value = value
            row.expires = expire_time
            row.save()

    def delete(self, key):
        doc = CacheRow.get_row(key)
        if doc:
            doc.delete()

    def get_many(self, keys):
        keys = map(smart_str, keys)
        return map(CacheRow.get_row, keys)

    def incr(self, key, delta=1):
        if key not in self:
            raise ValueError, "Key '%s' not found" % key
        new_value = self.get(key)['value'] + delta
        self.set(key, new_value)
        return new_value
