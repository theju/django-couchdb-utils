BASIC_TESTS = """
>>> from auth.models import User
>>> u = User(id='testuser', email='test@example.com', password='testpw')
>>> u.save()
>>> u.has_usable_password()
True
>>> u.check_password('bad')
False
>>> u.check_password('testpw')
True
>>> u.set_unusable_password()
>>> u.check_password('testpw')
False
>>> u.has_usable_password()
False
>>> u2 = User(id='testuser2', email='test2@example.com')
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
