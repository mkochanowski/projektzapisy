from django.test import TestCase
from .factories import UserFactory


class BaseUserTestCase(TestCase):

    def test_password_check(self):
        u = UserFactory()
        self.assertTrue(u.check_password('test'))
