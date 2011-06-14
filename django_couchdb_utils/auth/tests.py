BASIC_TESTS = """
>>> from django_couchdb_utils.auth.models import User
>>> from django.contrib.auth.models import UNUSABLE_PASSWORD
>>> u = User(username='testuser', email='test@example.com', password='testpw')
>>> u.set_password('testpw')
>>> u.save()
>>> u.has_usable_password()
True
>>> u.check_password('bad')
False
>>> u.check_password('testpw')
True
>>> u.set_unusable_password()
>>> u.has_usable_password()
False
>>> u2 = User(username='testuser2', email='test2@example.com')
>>> u2.password = UNUSABLE_PASSWORD
>>> u2.save()
>>> u2.has_usable_password()
False

>>> u.is_authenticated()
True
>>> u.is_staff
False
>>> u.is_active
True
>>> u.is_superuser
False
"""

__test__ = {
    'BASIC_TESTS': BASIC_TESTS,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()
