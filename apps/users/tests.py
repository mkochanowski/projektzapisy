# -*- coding: utf-8 -*-

# tests marked by comment "TIME DEPENDENCY" should be free from this dependency

from datetime import datetime, timedelta, date

from django.test import TestCase
from django.contrib.auth.models import User

from apps.enrollment.records.models import Record
from apps.enrollment.courses.models import Course, Term, Group
from apps.users.models import Employee, Student, StudiaZamawiane
from apps.users.exceptions import NonEmployeeException, NonStudentException
        
class EmployeeGroupsTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__courses']

    def setUp(self):
        self.user = User.objects.get(id=4)
    
    def testWithNotEmployeeUser(self):
        self.user.employee.delete()
        self.assertRaises(NonEmployeeException, Employee.get_all_groups, 4)
        
    def testEmployeeGroups(self):
        groups = Employee.get_all_groups(self.user.id)
        groups_id = [g.id for g in groups]
        self.assertEquals(groups_id, [1, 3, 5])
        
class EmployeeScheduleTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__courses']
    
    def setUp(self):
        self.user = User.objects.get(id=4)
        
    def testWithNotEmployeeUser(self):
        self.user.employee.delete()
        self.assertRaises(NonEmployeeException, Employee.get_schedule, self.user.id)
 
#TIME DEPENDENCY       
    def testEmployeeSchedule(self):
        course_1 = Course.objects.get(id=1)
        
        groups = Employee.get_schedule(self.user.id)
        
        term_1 = Term.objects.get(id=1).id
        term_2 = Term.objects.get(id=3).id
        
        groups_id = [g.id for g in groups]
        groups_course = [g.course_ for g in groups]
        groups_term_id = []
        groups_term = [groups_term_id.extend(t) for t in [g.terms_ for g in groups]]
        groups_term_id = map(lambda x: x.id, groups_term_id)
        
        for g in groups_id:
        	self.assert_(g in [1, 3, 5])
        for s in groups_course:
        	self.assert_(s in [course_1, course_1])
        for t in groups_term_id:
        	self.assert_(t in [term_1, term_2])
        
class StudentScheduleTest(TestCase):
    fixtures =  ['fixtures__users', 'fixtures__courses']
    
    def setUp(self):
    	"""
    	EXERCISE_GROUP:
	    	"fields": {
	            "limit": 120, 
	            "type": "2", 
	            "teacher": 3, 
	            "course": 1
	        }
	    LECTURE_GROUP:
		    "fields": {
	            "limit": 120, 
	            "type": "1", 
	            "teacher": 3, 
	            "course": 1
	        }
    	"""
        self.user = User.objects.get(id=5)
        self.exercise_group = Group.objects.get(id=1)
        self.lecture_group = Group.objects.get(id=3)
        self.lecture_group_2 = Group.objects.get(id=5)        
        #Automaticaly add student to lecture group
        self.record = Record.add_student_to_group(self.user.id, self.exercise_group.id)
        
#    def testWithNotStudentUser(self):
#        TODO: function changes, change test
#        self.user.student.delete()
#
#        self.assertRaises(NonStudentException, Student.get_schedule, self.user.student)

#TIME DEPENDENCY        
    def testStudentSchedule(self):
        course_1 = Course.objects.get(id=1)
        course_1.semester.date = datetime.now().year
        course_1.semester.semester_begining = date.today()
        course_1.semester.semester_ending = date.today() + timedelta(days = 5 * 30)
        course_1.semester.save()
        
        groups = Student.get_schedule(self.user.student)
        
        term_1 = Term.objects.get(id=1).id
        term_2 = Term.objects.get(id=3).id
        
        groups_id = [g.id for g in groups]
        groups_course = [g.course_ for g in groups]
        groups_term_id = []
        groups_term = [groups_term_id.extend(t) for t in [g.terms_ for g in groups]]
        groups_term_id = map(lambda x: x.id, groups_term_id)
        
        for g in groups_id:
        	self.assert_(g in [self.exercise_group.id, self.lecture_group.id, self.lecture_group_2.id])
        for s in groups_course:
        	self.assert_(s in [course_1, course_1])
        for t in groups_term_id:
        	self.assert_(t in [term_1, term_2])

class IBANTest(TestCase):
   def setUp(self):
	self.valid_polish = 'PL08109000049916589081209234'
	self.invalid_polish = 'PL08119000049916589081209234'
	self.not_alphanum = 'PL0810&000049916589081209234'
	self.without_country_code = '08109000049916589081209234'

   def testWithNotAlphaNumeric(self):
	self.assertFalse(StudiaZamawiane.check_iban(self.not_alphanum))

   def testWithoutCountryCode(self):
	self.assertFalse(StudiaZamawiane.check_iban(self.without_country_code))

   def testWithInvalidPolish(self):
	self.assertFalse(StudiaZamawiane.check_iban(self.invalid_polish))

   def testWithValidPolish(self):
	self.assert_(StudiaZamawiane.check_iban(self.valid_polish))
	

