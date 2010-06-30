# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User

from enrollment.records.models import Record
from enrollment.subjects.models import Subject, Term, Group
from users.models import Employee, Student
from users.exceptions import NonEmployeeException, NonStudentException

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
        self.assertRaises(NonEmployeeException, Employee.get_schedule, self.user.id)
        
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
        
class StudentScheduleTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']
    
    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group_1 = Group.objects.get(id=1)
        self.group_2 = Group.objects.get(id=3)
        self.record_1 = Record.add_student_to_group(self.user.id, self.group_1.id)
        self.record_2 = Record.add_student_to_group(self.user.id, self.group_2.id)
        
    def testWithNotStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Student.get_schedule, self.user.id)
        
    def testStudentSchedule(self):
        groups = Student.get_schedule(self.user.id)
        subject_1 = Subject.objects.get(id=1)
        term_1 = Term.objects.get(id=1).id
        term_2 = Term.objects.get(id=3).id
        
        groups_id = [g.id for g in groups]
        groups_subject = [g.subject_ for g in groups]
        groups_term_id = []
        groups_term = [groups_term_id.extend(t) for t in [g.terms_ for g in groups]]
        groups_term_id = map(lambda x: x.id, groups_term_id)
        
        self.assertEquals(groups_id, [self.group_1.id, self.group_2.id])
        self.assertEquals(groups_subject, [subject_1, subject_1])
        self.assertEquals(groups_term_id, [term_1, term_2])
        