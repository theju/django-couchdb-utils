=======
README
=======

This project's goal is to replace the RDBMS specific backends
used in Django with CouchDB_. It uses Coucchdbkit_ as a CouchDB-library

Currently it has a moderately tested:

* `Auth backend`_
* `Session backend`_
* `Cache backend`_ (not yet modified to work with Couchdbkit)
* OpenID consumer using CouchDB_ store (requires `django_openid`_, also not yet modified to work with Couchdbkit)

To use this library, install Couchdbkit and reference it in your INSTALLED_APPS in settings.py

.. _`CouchDB`: http://couchdb.apache.org/
.. _`Couchdbkit`: http://couchdbkit.org/
.. _`Auth backend`: http://docs.djangoproject.com/en/dev/topics/auth/#other-authentication-sources
.. _`Session backend`: http://docs.djangoproject.com/en/dev/topics/http/sessions/#configuring-the-session-engine
.. _`Cache backend`: http://docs.djangoproject.com/en/dev/topics/cache/#using-a-custom-cache-backend
.. _`django_openid`: http://github.com/simonw/django-openid/master/tree


========
INSTALL
========


General Instructions

* Reference the ``django_couchdb_utils`` app into your ``INSTALLED_APPS`` in ``settings.py``.

* To the COUCHDB_DATABASES (which is used by Couchdbkit) add::

    ('django_couchdb_utils', 'http://127.0.0.1:5984/somedb'),

  If your do not use Couchdbkit otherwise, just add the following to your ``settings.py``::

    COUCHDB_DATABASES = (
      ('yourapp.auth', 'http://127.0.0.1:5984/somedb'),
    )

  As the library doesn't make any assumptions about the Ids of the CouchDB
  objects it stores, it is safe to use it with an already existing database.



  * To enable authentication support add the ``AUTHENTICATION_BACKENDS`` attribute
    in ``settings.py`` like::

    AUTHENTICATION_BACKENDS = ('auth.backends.CouchDBAuthBackend',)

  * To enable cache support add the ``CACHE_BACKEND`` attribute in ``settings.py`` like::

    CACHE_BACKEND = "cache.couch://"

  * To enable sessions support add the ``SESSION_ENGINE`` attribute in ``settings.py`` like::

    SESSION_ENGINE = "sessions.couchdb_session"
