========
INSTALL
========

* Reference the ``auth`` app into your ``INSTALLED_APPS`` in ``settings.py``.
* Add the ``AUTHENTICATION_BACKENDS`` attribute in ``settings.py`` like::

    AUTHENTICATION_BACKENDS = ('auth.backends.CouchDBAuthBackend',)

* To the COUCHDB_DATABASES (which is used by Couchdbkit) add::

    ('yourapp.auth', 'http://127.0.0.1:5984/somedb'),

  If your do not use Couchdbkit otherwise, just add the following to your ``settings.py``::

    COUCHDB_DATABASES = (
      ('yourapp.auth', 'http://127.0.0.1:5984/somedb'),
    )

  As the library doesn't make any assumptions about the Ids of the CouchDB
  objects it stores, it is safe to use it with an already existing database.

