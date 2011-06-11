=======
README
=======

This project's goal is to replace the RDBMS specific backends used in Django
with `CouchDB`_ using `Couchdbkit`_.

Currently it has a moderately tested:

* `Auth backend`_
* `Session backend`_
* `Cache backend`_
* `Email Cache backend`_ wraps another email backend and caches mails that could not be sent
* OpenID consumer using `CouchDB`_ store (requires `django-openid`_)

To use this library, install Couchdbkit and reference it in your ``INSTALLED_APPS`` in ``settings.py``

.. _`CouchDB`: http://couchdb.apache.org/
.. _`Couchdbkit`: http://couchdbkit.org/
.. _`Auth backend`: http://docs.djangoproject.com/en/dev/topics/auth/#other-authentication-sources
.. _`Session backend`: http://docs.djangoproject.com/en/dev/topics/http/sessions/#configuring-the-session-engine
.. _`Cache backend`: http://docs.djangoproject.com/en/dev/topics/cache/#using-a-custom-cache-backend
.. _`Email Cache backend`: http://docs.djangoproject.com/en/dev/topics/email/
.. _`django-openid`: http://github.com/simonw/django-openid/master/tree


========
INSTALL
========


General Instructions

* Reference the ``django_couchdb_utils`` apps into your ``INSTALLED_APPS`` in ``settings.py``::

    ...
    "django_couchdb_utils.auth",
    "django_couchdb_utils.sessions",
    "django_couchdb_utils.cache",
    ...

* To the ``COUCHDB_DATABASES`` (which is used by Couchdbkit) add the couchdb utils apps that you plan to use::

    ('django_couchdb_utils_auth',     'http://127.0.0.1:5984/authdb'),
    ('django_couchdb_utils_sessions', 'http://127.0.0.1:5984/sessionsdb'),
    ('django_couchdb_utils_cache',    'http://127.0.0.1:5984/cachedb'),
    ...

  If your do not use Couchdbkit otherwise, just add the following to your ``settings.py``::

    COUCHDB_DATABASES = (
      ('django_couchdb_utils_auth', 'http://127.0.0.1:5984/somedb'),
      ...
    )

  As the library doesn't make any assumptions about the Ids of the CouchDB
  objects it stores, it is safe to use it with an already existing database.

* To enable authentication support add the ``AUTHENTICATION_BACKENDS`` attribute in ``settings.py`` like::

      AUTHENTICATION_BACKENDS = ('django_couchdb_utils.auth.backends.CouchDBAuthBackend',)

* To enable cache support add the ``CACHE_BACKEND`` attribute in ``settings.py`` like::

      CACHE_BACKEND = "cache.couch://"

* To enable sessions support add the ``SESSION_ENGINE`` attribute in ``settings.py`` like::

      SESSION_ENGINE = "django_couchdb_utils.sessions.couchdb"

* To enable the CouchDB email caching backend, set the ``EMAIL_BACKEND`` attribute in ``settings.py`` like::

      EMAIL_BACKEND = "django_couchdb_utils.email.CouchDBEmailBackend"

  # the backend that should be wrapped by the CouchDB caching backend
  COUCHDB_EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
