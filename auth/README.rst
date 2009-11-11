========
INSTALL
========

* Reference the auth app into your ``INSTALLED_APPS`` in ``settings.py``.
* Add it to the ``AUTHENTICATION_BACKENDS`` attribute in ``settings.py`` like::

    AUTHENTICATION_BACKENDS = ('auth.backends.CouchDBAuthBackend',)
* Add ``COUCHDB_HOST`` attribute to ``settings.py``::

    COUCHDB_HOST = "http://localhost:5984/"
* [[ Optional ]] If you plan to host multiple auth databases (say, of multiple django apps) of 
  a single CouchDB instance, then add a unique prefix::

    COUCHDB_AUTH_PREFIX = "site1_"