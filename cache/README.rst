========
INSTALL
========

* Reference the ``cache`` app into your ``INSTALLED_APPS`` in ``settings.py``.
* Add the ``CACHE_BACKEND`` attribute in ``settings.py`` like::

    CACHE_BACKEND = "cache.couch://"

* Add ``COUCHDB_HOST`` attribute to ``settings.py``::

    COUCHDB_HOST = "http://localhost:5984/"

* [[ Optional ]] If you plan to host multiple cache databases (say, of multiple 
  django apps) of a single CouchDB instance, then add a unique prefix::

    COUCHDB_CACHE_PREFIX = "site1_"