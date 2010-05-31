from django.test import TestCase
from django.contrib.auth.models import User

from enrollment.subjects.models import Subject, Group, StudentOptions
from enrollment.records.models import Record
from enrollment.records.exceptions import NonStudentException, NonGroupException, AlreadyAssignedException, OutOfLimitException, AlreadyNotAssignedException, AssignedInThisTypeGroupException, RecordsNotOpenException
from enrollment.subjects.exceptions import NonSubjectException

from users.models import Employee, Student

from datetime import datetime

class AddUserToGroupTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']

    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group = Group.objects.get(id=1)
        

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.add_student_to_group, self.user.id, self.group.id)

    def testWithoutGivenGroup(self):
        group_id = self.group.id
        self.group.delete()
        self.assertRaises(NonGroupException, Record.add_student_to_group, self.user.id, group_id)

    def testStudentAssignedToGroup(self):
        Record.add_student_to_group(self.user.id, self.group.id)
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
        
    def testSubjectWithRecordsNotOpenForStudent(self):
        self.user.student.records_opening_delay_hours = 0
        self.user.student.save()
        self.group.subject.semester.records_opening = datetime.now()
        self.group.subject.semester.save()
        student_options = StudentOptions.objects.get(student=self.user.student, subject=self.group.subject)
        student_options.records_opening_delay_hours = 10
        student_options.save()
        self.assertRaises(RecordsNotOpenException, Record.add_student_to_group, self.user.id, self.group.id)

class ChangeUserGroupTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']

    
    def setUp(self):
        self.user = User.objects.get(id=5)
        self.old_group = Group.objects.get(id=1)
        self.new_group = Group.objects.get(id=2)
        self.old_record = Record.add_student_to_group(self.user.id, self.old_group.id)
    
    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.change_student_group, self.user.id, self.old_group.id, self.new_group.id)
    
    def testWithoutGivenOldGroup(self):
        group_id = self.old_group.id
        self.old_group.delete()
        self.assertRaises(NonGroupException, Record.change_student_group, self.user.id, group_id, self.new_group.id)
    
    def testWithoutGivenNewGroup(self):
        group_id = self.new_group.id
        self.new_group.delete()
        self.assertRaises(NonGroupException, Record.change_student_group, self.user.id, self.old_group.id, group_id)
    
    def testStudentChangeGroup(self):
        new_record = Record.change_student_group(self.user.id, self.old_group.id, self.new_group.id)
        self.assertEqual(new_record.group, self.new_group)
        self.assertEqual(new_record.student, self.user.student)
        
    def testStudentNotAssignedChangeGroup(self):
        self.old_record.delete()
        self.assertEqual(Record.objects.count(), 0)
        self.assertRaises(AlreadyNotAssignedException, Record.change_student_group, self.user.id, self.old_group.id, self.new_group.id)
        self.assertEqual(Record.objects.count(), 0)
           
class RemoveUserToGroupTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']

        
    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group = Group.objects.get(id=1)
        self.record = Record.add_student_to_group(self.user.id, self.group.id)

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
 
class IsStudentInSubjectGroupTypeTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']

    
    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group = Group.objects.get(id=1)
        self.group2 = Group.objects.get(id=3)
        self.subject = Subject.objects.get(id=1)
        self.record = Record.add_student_to_group(self.user.id, self.group.id)
    
    def testWithNonStudent(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.is_student_in_subject_group_type, self.user.id, self.subject.slug, self.group.type)
        
    def testWithNonSubject(self):    
        subject_slug = self.subject.slug
        self.subject.delete()
        self.assertRaises(NonSubjectException, Record.is_student_in_subject_group_type, self.user.id, subject_slug, self.group.type)
    
    def testStudentInSubjectGroupType(self):
        self.assert_(Record.is_student_in_subject_group_type(self.user.id, self.subject.slug, self.group.type))
        self.assertFalse(Record.is_student_in_subject_group_type(self.user.id, self.subject.slug, self.group2.type))
                    
class GetGroupsForStudentTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']

    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group = Group.objects.get(id=1)
        self.record = Record.add_student_to_group(self.user.id, self.group.id)
    
    def testStudentAssignedToGroup(self):
        groups = Record.get_groups_for_student(self.user.id)
        self.assertEqual(groups, [self.group])
        
    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Record.get_groups_for_student, self.user.id)
        
class GetStudentsInGroupTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']
    
    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group = Group.objects.get(id=1)
        self.record = Record.add_student_to_group(self.user.id, self.group.id)
    
    def testStudentAssignedToGroup(self):
        students = Record.get_students_in_group(self.group.id)
        self.assertEqual(students, [self.user.student])
        
    def testWithNonExistsGroup(self):
        self.group.delete()
        self.assertRaises(NonGroupException, Record.get_students_in_group, self.group.id)

class AssignmentToGroupsWithSameTypes(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']
    
    def setUp(self):
        self.user = User.objects.get(id=5)

        self.group1 = Group.objects.get(id=1)
        self.group2 = Group.objects.get(id=2)
        self.lecture1 = Group.objects.get(id=3)
        self.lecture2 = Group.objects.get(id=4)

        self.record = Record.objects.create(student=self.user.student, group=self.lecture1)

    def testAssignToAnotherLecture(self):
        Record.add_student_to_group(self.user.id, self.lecture2.id) 
        self.assertEqual(Record.objects.count(), 2)

    def testAssignToGroupForFirstTime(self):
        Record.add_student_to_group(self.user.id, self.group1.id)
        self.assertEqual(Record.objects.count(), 2)
		
    def testAssignToCurrentlyBookedGroupWithSameType(self):
        Record.add_student_to_group(self.user.id, self.group1.id)
        self.assertRaises(AssignedInThisTypeGroupException, Record.add_student_to_group, self.user.id, self.group2.id)

    
