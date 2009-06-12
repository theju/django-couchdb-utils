=======
README
=======

This project's goal is to replace the RDBMS specific backends 
used in django with document-oriented databases (more 
specifically CouchDB_).

Currently it has a moderately tested:

* `Auth backend`_
* `Session backend`_

In the future, I plan to work on (no guarantees that I might
have a success on the one's listed below, but they are worth
a try):

* `Cache backend`_
* Admin backend
* Database backend
and anything else I forgot but you might love to use...

Please do leave your feedback if you found the project worthless
or useful (by any chance).

.. _`CouchDB`: http://couchdb.apache.org/
.. _`Auth backend`: http://docs.djangoproject.com/en/dev/topics/auth/#other-authentication-sources
.. _`Session backend`: http://docs.djangoproject.com/en/dev/topics/http/sessions/#configuring-the-session-engine
.. _`Cache backend`: http://docs.djangoproject.com/en/dev/topics/cache/#using-a-custom-cache-backend
