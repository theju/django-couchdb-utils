========
INSTALL
========

* Install Couchdbkit from http://couchdbkit.org/
* Reference both ``couchdbkit`` and ``auth`` in your ``INSTALLED_APPS`` in ``settings.py``.
* Add the ``AUTHENTICATION_BACKENDS`` attribute in ``settings.py`` like::

    AUTHENTICATION_BACKENDS = ('auth.backends.CouchDBAuthBackend',)

* To the COUCHDB_DATABASES (which is used by Couchdbkit) add::

    ('yourapp.auth', 'http://127.0.0.1:5984/auth'),

  If your do not use Couchdbkit otherwise, just add the following to your ``settings.py``::

    COUCHDB_DATABASES = (
      ('authttest.auth', 'http://127.0.0.1:5984/auth'),
    )

