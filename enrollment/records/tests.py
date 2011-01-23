# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User

from enrollment.subjects.models import Subject, Group, StudentOptions, Semester
from enrollment.records.models import Record, Queue
from enrollment.records.exceptions import NonStudentException, NonGroupException, AlreadyAssignedException, OutOfLimitException, AlreadyNotAssignedException, AssignedInThisTypeGroupException, RecordsNotOpenException, AlreadyQueuedException
from enrollment.subjects.exceptions import NonSubjectException
from users.models import Employee, Student

from datetime import datetime, timedelta

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
        self.assertEqual(Record.objects.count(), 0)
        Record.add_student_to_group(self.user.id, self.group.id)
        self.assertEqual(Record.objects.count(), 2)
        Record.add_student_to_group(self.user.id, self.group.id)
        self.assertEqual(Record.objects.count(), 2)

    def testStudentNotAssignedToGroup(self):
        self.assertEqual(Record.objects.count(), 0)
        Record.add_student_to_group(self.user.id, self.group.id)
        self.assertEqual(Record.objects.count(), 2)

    def testGroupWithStudentLimitExceeded(self):
        self.group.limit = 0
        self.group.save()
        self.assertRaises(OutOfLimitException, Record.add_student_to_group, self.user.id, self.group.id)
        
    def testSubjectWithRecordsNotOpenForStudent(self):
        self.user.student.records_opening_delay_minutes = 0
        self.user.student.save()
        self.group.subject.semester.records_opening = datetime.now()
        self.group.subject.semester.records_closing = datetime.now()
        self.group.subject.semester.save()
        student_options = StudentOptions.objects.get(student=self.user.student, subject=self.group.subject)
        student_options.records_opening_delay_minutes = 10
        student_options.save()
        self.assertRaises(RecordsNotOpenException, Record.add_student_to_group, self.user.id, self.group.id)

           
class RemoveUserFromGroupTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']

        
    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group = Group.objects.get(id=3)
        self.records = Record.add_student_to_group(self.user.id, self.group.id)

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
        self.records[0].delete()
        self.assertEqual(Record.objects.count(), 0)
        self.assertRaises(AlreadyNotAssignedException, Record.remove_student_from_group, self.user.id, self.group.id)
        self.assertEqual(Record.objects.count(), 0)
 
class IsStudentInSubjectGroupTypeTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__subjects']

    
    def setUp(self):
        self.user = User.objects.get(id=5)
        self.group = Group.objects.get(id=3)
        self.group2 = Group.objects.get(id=1)
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
        self.group = Group.objects.get(id=3)
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
        self.assertEqual(Record.objects.count(), 1)
        Record.add_student_to_group(self.user.id, self.group1.id)
        self.assertEqual(Record.objects.count(), 2)
        Record.add_student_to_group(self.user.id, self.group2.id)
        self.assertEqual(Record.objects.count(), 2)
        
class MoveStudentFromQueueToGroup(TestCase):
    fixtures =  ['fixtures__priority_queue']
    
    def setUp(self):
        self.student_to_remove = User.objects.get(id=100)
        self.student_to_remove2 = User.objects.get(id=104)
        self.student_first_in_queue = User.objects.get(id=101)
        self.student_second_in_queue = User.objects.get(id=102)
        self.full_group = Group.objects.get(id=100)
        self.same_type_group = Group.objects.get(id=101)
        self.other_type_group = Group.objects.get(id=102)
        self.same_type_group_hp = Group.objects.get(id=103)
        self.same_type_group_ep = Group.objects.get(id=104)
        self.empty_queue_group = Group.objects.get(id=105)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()
    

    def testEmptyQueue(self):
        self.assertEqual(Record.objects.filter(group=self.empty_queue_group.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove.id, self.empty_queue_group.id)
        self.assertEqual(Record.objects.filter(group=self.empty_queue_group.id).count(), 0)
        self.assertEqual(Queue.objects.filter(group=self.empty_queue_group.id).count(), 0)
        
    def testNotEmptyQueue(self):
        Record.remove_student_from_group(self.student_to_remove.id, self.full_group.id)
        self.assertEqual(Record.objects.filter(student=self.student_to_remove.id, group=self.full_group.id).count(), 0)
        self.assertEqual(Record.objects.filter(student=self.student_first_in_queue.id, group=self.full_group.id).count(), 1)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.full_group.id).count(), 0)
    
    def testRemoveStudentLowerPriorityRecords(self):
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove.id, self.full_group.id)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group.id).count(), 0)
        
    def testRemoveStudentEqualPriorityRecords(self):
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_ep.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove.id, self.full_group.id)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_ep.id).count(), 0)

    def testNotRemoveStudentLowerPriorityRecordsWithOtherGroupType(self):
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.other_type_group.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove.id, self.full_group.id)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.other_type_group.id).count(), 1)
        
    def testNotRemoveStudentHigherPriorityRecords(self):
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_hp.id).count(), 1)
        Record.remove_student_from_group(self.student_to_remove.id, self.full_group.id)
        self.assertEqual(Queue.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_hp.id).count(), 1)
        
    def testChangeStudentGroup(self):
        """ if student is enrolled to some group and there is a free place in the same type group and student is in that group queue than enroll student to group"""
        Record.remove_student_from_group(self.student_to_remove.id, self.full_group.id)
        Record.remove_student_from_group(self.student_to_remove2.id, self.same_type_group_hp.id)
        self.assertEqual(Record.objects.filter(student=self.student_first_in_queue.id, group=self.full_group.id).count(), 0)
        self.assertEqual(Record.objects.filter(student=self.student_first_in_queue.id, group=self.same_type_group_hp.id).count(), 1)
    


class GetStudentsInQueue(TestCase):
    fixtures =  ['fixtures__queue']
    
    def setUp(self):
        self.user = User.objects.get(id=100)
        self.student = User.objects.get(id=100)
        self.group = Group.objects.get(id=100)
        self.group2 = Group.objects.get(id=103)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()
        
    def testWithoutGivenGroup(self):
        group_id = self.group.id
        self.group.delete()
        self.assertRaises(NonGroupException, Queue.get_students_in_queue, group_id)
    
    def testWithEmptyGroup(self):
        self.assertEqual(Queue.objects.filter(group=100).count(), 0)
        queued_students = Queue.get_students_in_queue(self.group.id)
        self.assertEqual(len(queued_students),0)
    
    def testWithNonEmptyGroup(self):
        queued_students = Queue.get_students_in_queue(self.group2.id)
        self.assertEqual(len(queued_students),3)

class AddStudentToQueue(TestCase):
    fixtures =  ['fixtures__queue']
    
    def setUp(self):
        self.user = User.objects.get(id=100)
        self.student = User.objects.get(id=100)
        self.employee = User.objects.get(id=1000)
        self.group = Group.objects.get(id=100)
        self.group2 = Group.objects.get(id=101)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Queue.add_student_to_queue, self.user.id, self.group.id)

    def testWithoutGivenGroup(self):
        group_id = self.group.id
        self.group.delete()
        self.assertRaises(NonGroupException, Queue.add_student_to_queue, self.student.id, group_id)

    def testStudentAssignedToGroup(self):
        Record.add_student_to_group(self.student.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 0)
        self.assertRaises(AlreadyAssignedException, Queue.add_student_to_queue, self.student.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 0)
    
    def testStudentNotAssignedToQueue(self):
        Queue.add_student_to_queue(self.student.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 1)
    

    def testStudenAssignedToQueue(self):
        Queue.add_student_to_queue(self.student.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 1)
        self.assertRaises(AlreadyQueuedException, Queue.add_student_to_queue, self.student.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 1)
          
        '''def testWithRecordsNotOpenForStudent(self):
        self.user.student.records_opening_delay_minutes = 0
        self.user.student.save()
        self.group.subject.semester.records_opening = datetime.now()
        self.group.subject.semester.records_closing = datetime.now()
        self.group.subject.semester.save()
        student_options = StudentOptions.objects.get(student=self.user.student, subject=self.group.subject)
        student_options.records_opening_delay_minutes = 10
        student_options.save()
        self.assertRaises(RecordsNotOpenException, Queue.add_student_to_queue, self.user.id, self.group.id)'''

class RemoveStudentFromQueue(TestCase):
    fixtures =  ['fixtures__queue']
    
    def setUp(self):
        self.user = User.objects.get(id=101)
        self.student1 = User.objects.get(id=100)
        self.student2 = User.objects.get(id=101)
        self.employee = User.objects.get(id=1000)
        self.group = Group.objects.get(id=101)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()

    def testWithNonStudentUser(self):
        self.user.student.delete()
        self.assertRaises(NonStudentException, Queue.remove_student_from_queue, self.user.id, self.group.id)

    def testWithoutGivenGroup(self):
        group_id = self.group.id
        self.group.delete()
        self.assertRaises(NonGroupException, Queue.remove_student_from_queue, self.student1.id, group_id)
    
    def testStudentNotAssignedToQueue(self):
        self.assertRaises(AlreadyNotAssignedException, Queue.remove_student_from_queue, self.student1.id, self.group.id)
    
    def testStudenAssignedToQueue(self):
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 1)
        Queue.remove_student_from_queue(self.student2.id, self.group.id)
        self.assertEqual(Queue.objects.filter(group=self.group.id).count(), 0)
        
class RemoveFirstStudentFromQueue(TestCase):
    fixtures =  ['fixtures__queue']
    
    def setUp(self):
        self.user = User.objects.get(id=101)
        self.student1 = User.objects.get(id=100)
        self.student2 = User.objects.get(id=101)
        self.student3 = User.objects.get(id=102)
        self.student4 = User.objects.get(id=105)
        self.employee = User.objects.get(id=1000)
        self.group = Group.objects.get(id=100)
        self.group2 = Group.objects.get(id=103)
        self.group3 = Group.objects.get(id=104)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()


    def testWithoutGivenGroup(self):
        group_id = self.group2.id
        self.group2.delete()
        self.assertRaises(NonGroupException, Queue.remove_first_student_from_queue, group_id)
    
    def testEmptyQueue(self):
        self.assertEqual(Queue.remove_first_student_from_queue(self.group.id),False)
    
    def testStudenAssignedToQueue(self):
        removed = Queue.objects.get(group=self.group2.id, student=self.student2.id).student
        self.assertEqual(Queue.remove_first_student_from_queue(self.group2.id).student,removed)
    
    def testWithEctsLimitExceeded(self):
        removed = Queue.objects.get(group=self.group3.id, student=self.student4.id).student
        self.assertEqual(Queue.remove_first_student_from_queue(self.group3.id).student,removed)

class RemoveStudentLowPriorityRecords(TestCase):
    fixtures =  ['fixtures__queue']
    
    def setUp(self):
        self.user = User.objects.get(id=101)
        self.student1 = User.objects.get(id=100)
        self.student2 = User.objects.get(id=101)
        self.student3 = User.objects.get(id=102)
        self.employee = User.objects.get(id=1000)
        self.group = Group.objects.get(id=100)
        self.group2 = Group.objects.get(id=103)
        self.semester=Semester.objects.get(id=100)
        self.semester.records_opening = datetime.now()
        self.semester.records_closing = datetime.now() + timedelta(days=7)
        self.semester.save()


    def testWithoutGivenGroup(self):
        group_id = self.group2.id
        self.group2.delete()
        self.assertRaises(NonGroupException, Queue.remove_student_low_priority_records, self.student1.id, group_id, 10)

    def testStudenAssignedToQueue(self):
        Queue.remove_student_low_priority_records(self.student2.id, self.group2.id,10)
        self.assertEqual(Queue.objects.filter(group=101, student=self.student2).count(), 0)
    
    
