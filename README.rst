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

* Reference the ``django_couchdb_utils`` app into your ``INSTALLED_APPS`` in ``settings.py``.

* To the ``COUCHDB_DATABASES`` (which is used by Couchdbkit) add::

    ('django_couchdb_utils', 'http://127.0.0.1:5984/somedb'),

  If your do not use Couchdbkit otherwise, just add the following to your ``settings.py``::

    COUCHDB_DATABASES = (
      ('django_couchdb_utils', 'http://127.0.0.1:5984/somedb'),
    )

  As the library doesn't make any assumptions about the Ids of the CouchDB
  objects it stores, it is safe to use it with an already existing database.

* To enable authentication support add the ``AUTHENTICATION_BACKENDS`` attribute in ``settings.py`` like::

      AUTHENTICATION_BACKENDS = ('django_couchdb_utils.auth.backends.CouchDBAuthBackend',)

* To enable cache support add the ``CACHE_BACKEND`` attribute in ``settings.py`` like::

      CACHE_BACKEND = "django_couchdb_utils.cache...."

* To enable sessions support add the ``SESSION_ENGINE`` attribute in ``settings.py`` like::

      SESSION_ENGINE = "django_couchdb_utils.sessions.couchdb_session"

* To enable the CouchDB email caching backend, set the ``EMAIL_BACKEND`` attribute in ``settings.py`` like::

      EMAIL_BACKEND = "django_couchdb_utils.email.CouchDBEmailBackend"

  # the backend that should be wrapped by the CouchDB caching backend
  COUCHDB_EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
