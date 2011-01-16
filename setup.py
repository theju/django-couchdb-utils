# -*- coding: utf-8 -*-

from distutils.core import setup
import os

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('django_couchdb_utils'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[len('django_couchdb_utils/'):] # Strip "django_couchdb_utils/"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name='django-couchdb-utils',
      version='0.1',
      description='A CouchDB-based replacement for some django.contrib modules',
      author=u'Stefan Kögl',
      author_email='stefan@skoegl.net',
      url='https://github.com/stefankoegl/django-couchdb-utils',
      download_url='https://github.com/stefankoegl/django-couchdb-utils',
      package_dir={'django_couchdb_utils': 'django_couchdb_utils'},
      packages=packages,
      package_data={'django_couchdb_utils': data_files},
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      )
