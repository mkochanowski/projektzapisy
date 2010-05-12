from django.test import TestCase
from django.contrib.auth.models import User

from offer.proposal.models import Proposal

#dopisac

from models import Record
from enrollment.records.exceptions import NonStudentException, NonGroupException, AlreadyAssignedException, OutOfLimitException, AlreadyNotAssignedException, AssignedInThisTypeGroupException


from users.models import Employee, Student

class FansTest(TestCase):
    def setUp(self):
        self.firstUser = User.objects.get(id=1)
        self.secondUser = User.objects.get(id=2)
        self.proposal = Proposal.objects.get(id=1)

    def testUserJoinToFans(self):
        self.proposal.addUserToFans(self.firstUser)
        self.assertEqual(self.proposal.fans.count(), 1)

    def testUserJoinToFans2(self):
        self.assertRaises(IsFanException, self.proposal.addUserToFans, self.firstUser)

    def testUsersJoinToFans(self):
        self.proposal.addUserToFans(self.firstUser)
        self.proposal.addUserToFans(self.secondUser)
        self.assertEqual(self.proposal.fans.count(), 2)

    def testUserStopBeFan1(self):
        self.proposal.addUserToFans(self.firstUser)
        self.proposal.deleteUserFromFans(self.firstUser)
        self.assertEqual(self.proposal.fans.all().count(), 0)

    def testUserStopBeFan2(self):
        self.proposal.addUserToFans(self.firstUser)
        self.proposal.addUserToFans(self.secondUser)
        self.proposal.deleteUserFromFans(self.firstUser)
        self.assertEqual(self.proposal.fans.all().count(), 1)

# sprawdzanie uprawnien:
    def testUserIsntFan(self):
        self.firstUser.student.delete()
        self.assertRaises(NonStudentException, self.proposal.addUserToFans, self.firstUser)
    def testUserIsntFan(self):
        self.firstUser.student.delete()
        self.assertRaises(NonStudentException, self.proposal.deleteUserToFans, self.firstUser)
        
class TeachersTest(TestCase):
    def setUp(self):
        self.firstUser = User.objects.get(id=1)
        self.secondUser = User.objects.get(id=2)
        self.proposal = Proposal.objects.get(id=1)
    def testUserJoinToTeachers(self):
        self.proposal.addUserToTeachers(self.firstUser)
        self.assertEqual(self.proposal.Teachers.count(), 1)

    def testUserJoinToTeachers2(self):
        self.assertRaises(IsTeacherException, self.proposal.addUserToTeachers, self.firstUser)

    def testUsersJoinToTeachers(self):
        self.proposal.addUserToTeachers(self.firstUser)
        self.proposal.addUserToTeachers(self.secondUser)
        self.assertEqual(self.proposal.Teachers.count(), 2)

    def testUserStopBeTeacher1(self):
        self.proposal.addUserToTeachers(self.firstUser)
        self.proposal.deleteUserFromTeachers(self.firstUser)
        self.assertEqual(self.proposal.Teachers.count(), 0)

    def testUserStopBeTeacher2(self):
        self.proposal.addUserToTeachers(self.firstUser)
        self.proposal.addUserToTeachers(self.secondUser)
        self.proposal.deleteUserFromTeachers(self.firstUser)
        self.assertEqual(self.proposal.Teachers.count(), 1)

# sprawdzanie uprawnien:
    def testUserIsntTeacher1(self):
        self.firstUser.employee.delete()
        self.assertRaises(NonEmployeeException, self.proposal.addUserToTeachers, self.firstUser)
    def testUserIsntTeacher2(self):
        self.firstUser.employee.delete()
        self.assertRaises(NonEmployeeException, self.proposal.deleteUserToTeachers, self.firstUser)