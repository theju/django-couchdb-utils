========
INSTALL
========

.. note:: 

     * This package depends on `django-openid`_. You need to install
       it first to be able to use the couchdb openid-consumer.
     * Other dependencies are the ``auth`` and ``session`` apps available
       as a part of `django-couchdb-utils`_.

* Install the ``auth`` and ``session`` (optional if you plan to use the
  ``CookieConsumer``) as per instructions provided in them.
* Set the ``COUCHDB_HOST`` attribute in ``settings.py`` like ::

    COUCHDB_HOST = "http://localhost:5984/

* Set the ``COUCHDB_OPENID_DB`` attribute in ``settings.py``::

    COUCHDB_OPENID_DB = "openid"

* If you plan to use the openid-consumer for multiple apps on different sites,
  it is recommended you set a unique prefix to prevent mixing of the ids::

    COUCHDB_OPENID_PREFIX = "site1_"

* Follow the instructions mentioned in the `django-openid`_ docs_ for further 
  details.


.. _`django-openid`: http://github.com/simonw/django-openid/master/tree
.. _`django-couchdb-utils`: http://github.com/theju/django-couchdb-utils/master/tree
.. _docs: http://github.com/simonw/django-openid/tree/master/django_openid/docs/