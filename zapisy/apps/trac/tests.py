"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User

from django.test import TestCase
from apps.trac.models import Issue


class VisibleLevelTest(TestCase):

    def setUp(self):
        #employee
        self.user1 = User.objects.create_user('user1')
        #admin
        self.user2 = User.objects.create_superuser('user2', 'aaa@aaa.pl', 'aaa')
        #student
        self.user3 = User.objects.create_user('user3')

        self.issue1 = Issue.objects.create(author=self.user1)

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
