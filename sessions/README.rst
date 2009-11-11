========
INSTALL
========

* Reference the ``sessions`` app into your ``INSTALLED_APPS`` in ``settings.py``.
* Add the ``SESSION_ENGINE`` attribute in ``settings.py`` like::

    SESSION_ENGINE = "sessions.couchdb_session"

* Add ``COUCHDB_HOST`` attribute to ``settings.py``::

    COUCHDB_HOST = "http://localhost:5984/"

* [[ Optional ]] If you plan to host multiple session databases (say, of multiple 
  django apps) of a single CouchDB instance, then add a unique prefix::

    COUCHDB_SESSION_PREFIX = "site1_"