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
