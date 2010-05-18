# -*- coding: utf-8 -*-

from django.test import TestCase
#from users.models import Employee, Student

class SimpleUserTest(TestCase):

    def setUp(self):
        pass
    
    def testOfNothing(self):
        self.assertEqual(0, 0)
