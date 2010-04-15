from django.test import TestCase
from django.contrib.auth.models import User

from enrollment.subjects.models import Group, Subject
from models import Record
from exceptions import NonStudentException, NonGroupException, AlreadyAssignedException, OutOfLimitException, AlreadyNotAssignedException

from users.models import Employee, Student

import mox

class AddUserToGroupTest(TestCase):
    fixtures = ['user_and_group']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.group = Group.objects.get(id=1)

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.add_student_to_group, self.user.id, self.group.id)

    def testWithoutGivenGroup(self):
        group_id = self.group.id
        self.group.delete()
        self.assertRaises(NonGroupException, Record.add_student_to_group, self.user.id, group_id)

    def testStudentAssignedToGroup(self):
        Record.objects.create(student=self.user.student, group=self.group)
        self.assertEqual(Record.objects.count(), 1)
        self.assertRaises(AlreadyAssignedException, Record.add_student_to_group, self.user.id, self.group.id)
        self.assertEqual(Record.objects.count(), 1)

    def testStudentNotAssignedToGroup(self):
        Record.add_student_to_group(self.user.id, self.group.id)
        self.assertEqual(Record.objects.count(), 1)

    def testGroupWithStudentLimitExceeded(self):
        self.group.limit = 0
        self.group.save()
        self.assertRaises(OutOfLimitException, Record.add_student_to_group, self.user.id, self.group.id)

class RemoveUserToGroupTest(TestCase):
    fixtures = ['user_and_group']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.group = Group.objects.get(id=1)
        self.record = Record.objects.create(student=self.user.student, group=self.group)

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.remove_student_from_group, self.user.id, self.group.id)

    def testWithoutGivenGroup(self):
        group_id = self.group.id
        self.group.delete()
        self.assertRaises(NonGroupException, Record.remove_student_from_group, self.user.id, group_id)

    def testStudentAssignedToGroup(self):
        Record.remove_student_from_group(self.user.id, self.group.id)
        self.assertEqual(Record.objects.count(), 0)

    def testStudentNotAssignedToGroup(self):
        self.record.delete()
        self.assertEqual(Record.objects.count(), 0)
        self.assertRaises(AlreadyNotAssignedException, Record.remove_student_from_group, self.user.id, self.group.id)
        self.assertEqual(Record.objects.count(), 0)
