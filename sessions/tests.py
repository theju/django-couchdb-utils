r"""

>>> from django.conf import settings
>>> from sessions.couchdb_session import SessionStore as CouchDBSession
>>> from django.contrib.sessions.backends.base import SessionBase

>>> session = CouchDBSession()
>>> session.modified
False
>>> session.get('cat')
>>> session['cat'] = "dog"
>>> session.modified
True
>>> session.pop('cat')
'dog'
>>> session.pop('some key', 'does not exist')
'does not exist'
>>> session.save(must_create=True)
>>> session.exists(session.session_key)
True
>>> session.delete(session.session_key)
>>> session.exists(session.session_key)
False

>>> session['foo'] = 'bar'
>>> session.save(must_create=True)
>>> session.exists(session.session_key)
True
>>> prev_key = session.session_key
>>> session.flush()
>>> session.exists(prev_key)
False
>>> session.session_key == prev_key
False
>>> session.modified, session.accessed
(True, True)
>>> session['a'], session['b'] = 'c', 'd'
>>> session.save()
>>> prev_key = session.session_key
>>> prev_data = session.items()
>>> session.cycle_key()
>>> session.session_key == prev_key
False
>>> session.items() == prev_data
True

>>> session = CouchDBSession(session.session_key)
>>> session.save()
>>> CouchDBSession('1').get('cat')

>>> s = SessionBase()
>>> s._session['some key'] = 'exists' # Pre-populate the session with some data
>>> s.accessed = False   # Reset to pretend this wasn't accessed previously

>>> s.accessed, s.modified
(False, False)

>>> s.pop('non existant key', 'does not exist')
'does not exist'
>>> s.accessed, s.modified
(True, False)

>>> s.setdefault('foo', 'bar')
'bar'
>>> s.setdefault('foo', 'baz')
'bar'

>>> s.accessed = False  # Reset the accessed flag

>>> s.pop('some key')
'exists'
>>> s.accessed, s.modified
(True, True)

>>> s.pop('some key', 'does not exist')
'does not exist'


>>> s.get('update key', None)

# test .update()
>>> s.modified = s.accessed = False   # Reset to pretend this wasn't accessed previously
>>> s.update({'update key':1})
>>> s.accessed, s.modified
(True, True)
>>> s.get('update key', None)
1

# test .has_key()
>>> s.modified = s.accessed = False   # Reset to pretend this wasn't accessed previously
>>> s.has_key('update key')
True
>>> s.accessed, s.modified
(True, False)

# test .values()
>>> s = SessionBase()
>>> s.values()
[]
>>> s.accessed
True
>>> s['x'] = 1
>>> s.values()
[1]

# test .iterkeys()
>>> s.accessed = False
>>> i = s.iterkeys()
>>> hasattr(i,'__iter__')
True
>>> s.accessed
True
>>> list(i)
['x']

# test .itervalues()
>>> s.accessed = False
>>> i = s.itervalues()
>>> hasattr(i,'__iter__')
True
>>> s.accessed
True
>>> list(i)
[1]

# test .iteritems()
>>> s.accessed = False
>>> i = s.iteritems()
>>> hasattr(i,'__iter__')
True
>>> s.accessed
True
>>> list(i)
[('x', 1)]

# test .clear()
>>> s.modified = s.accessed = False
>>> s.items()
[('x', 1)]
>>> s.clear()
>>> s.items()
[]
>>> s.accessed, s.modified
(True, True)

#########################
# Custom session expiry #
#########################

>>> from django.conf import settings
>>> from datetime import datetime, timedelta

>>> td10 = timedelta(seconds=10)

# A normal session has a max age equal to settings
>>> s.get_expiry_age() == settings.SESSION_COOKIE_AGE
True

# So does a custom session with an idle expiration time of 0 (but it'll expire
# at browser close)
>>> s.set_expiry(0)
>>> s.get_expiry_age() == settings.SESSION_COOKIE_AGE
True

# Custom session idle expiration time
>>> s.set_expiry(10)
>>> delta = s.get_expiry_date() - datetime.now()
>>> delta.seconds in (9, 10)
True
>>> age = s.get_expiry_age()
>>> age in (9, 10)
True

# Custom session fixed expiry date (timedelta)
>>> s.set_expiry(td10)
>>> delta = s.get_expiry_date() - datetime.now()
>>> delta.seconds in (9, 10)
True
>>> age = s.get_expiry_age()
>>> age in (9, 10)
True

# Custom session fixed expiry date (fixed datetime)
>>> s.set_expiry(datetime.now() + td10)
>>> delta = s.get_expiry_date() - datetime.now()
>>> delta.seconds in (9, 10)
True
>>> age = s.get_expiry_age()
>>> age in (9, 10)
True

# Set back to default session age
>>> s.set_expiry(None)
>>> s.get_expiry_age() == settings.SESSION_COOKIE_AGE
True

# Allow to set back to default session age even if no alternate has been set
>>> s.set_expiry(None)


# We're changing the setting then reverting back to the original setting at the
# end of these tests.
>>> original_expire_at_browser_close = settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
>>> settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Custom session age
>>> s.set_expiry(10)
>>> s.get_expire_at_browser_close()
False

# Custom expire-at-browser-close
>>> s.set_expiry(0)
>>> s.get_expire_at_browser_close()
True

# Default session age
>>> s.set_expiry(None)
>>> s.get_expire_at_browser_close()
False

>>> settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Custom session age
>>> s.set_expiry(10)
>>> s.get_expire_at_browser_close()
False

# Custom expire-at-browser-close
>>> s.set_expiry(0)
>>> s.get_expire_at_browser_close()
True

# Default session age
>>> s.set_expiry(None)
>>> s.get_expire_at_browser_close()
True

>>> settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = original_expire_at_browser_close
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
