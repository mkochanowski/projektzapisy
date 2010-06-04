# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User

from enrollment.subjects.models import Subject, Term
from users.models import Employee
from users.exceptions import NonEmployeeException

class SimpleUserTest(TestCase):

    def setUp(self):
        pass
    
    def testOfNothing(self):
        self.assertEqual(0, 0)
        
class EmployeeGroupsTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']

    def setUp(self):
        self.user = User.objects.get(id=4)
    
    def testWithNotEmployeeUser(self):
        self.user.employee.delete()
        self.assertRaises(NonEmployeeException, Employee.get_all_groups, self.user.id)
        
    def testEmployeeGroups(self):
        groups = Employee.get_all_groups(self.user.id)
        groups_id = [g.id for g in groups]
        self.assertEquals(groups_id, [1,3])
        
class EmployeeScheduleTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']
    
    def setUp(self):
        self.user = User.objects.get(id=4)
        
    def testWithNotEmployeeUser(self):
        self.user.employee.delete()
        self.assertRaises(NonEmployeeException, Employee.get_all_groups, self.user.id)
        
    def testEmployeeSchedule(self):
        groups = Employee.get_schedule(self.user.id)
        subject_1 = Subject.objects.get(id=1)
        term_1 = Term.objects.get(id=1).id
        term_2 = Term.objects.get(id=3).id
        
        groups_id = [g.id for g in groups]
        groups_subject = [g.subject_ for g in groups]
        groups_term_id = []
        groups_term = [groups_term_id.extend(t) for t in [g.terms_ for g in groups]]
        groups_term_id = map(lambda x: x.id, groups_term_id)
        
        self.assertEquals(groups_id, [1,3])
        self.assertEquals(groups_subject, [subject_1, subject_1])
        self.assertEquals(groups_term_id, [term_1, term_2])
        