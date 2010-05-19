# -*- coding:utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Employee, Student
from offer.proposal.models import Proposal
from offer.proposal.exceptions import *


class ProposalFansTest(TestCase):
    fixtures = ['fixtures__proposal_users.json', 'fixtures__proposal.json']
    
    def setUp(self):
        self.firstUser  = User.objects.get(pk=5)
        self.secondUser = User.objects.get(pk=6)
        self.thirdUser  = User.objects.get(pk=3) 
        self.proposall = Proposal.objects.get( name='Kurs 1' )

    def testUserJoinToFans(self):
        self.proposall.addUserToFans(self.firstUser)
        self.assertEqual(self.proposall.fans.count(), 1)

    def testUsersJoinToFans(self):
        self.proposall.addUserToFans(self.firstUser)
        self.proposall.addUserToFans(self.secondUser)
        self.assertEqual(self.proposall.fans.count(), 2)

    def testUserStopBeFan1(self):
        self.proposall.addUserToFans(self.firstUser)
        self.proposall.deleteUserFromFans(self.firstUser)
        self.assertEqual(self.proposall.fans.all().count(), 0)

    def testUserStopBeFan2(self):
        self.proposall.addUserToFans(self.firstUser)
        self.proposall.addUserToFans(self.secondUser)
        self.proposall.deleteUserFromFans(self.firstUser)
        self.assertEqual(self.proposall.fans.all().count(), 1)

# sprawdzanie uprawnien:
    def testUserIsntFan(self):
        self.assertRaises(NonStudentException, self.proposall.addUserToFans, self.thirdUser)
    def testUserIsntFan2(self):
        self.assertRaises(NonStudentException, self.proposall.deleteUserFromFans, self.thirdUser)
        
class ProposalTeachersTest(TestCase):
    fixtures = ['fixtures__users.json', 'fixtures__proposal.json']
    
    def setUp(self):
        self.firstUser  = User.objects.get(pk=4)
        self.secondUser = User.objects.get(pk=3)
        self.thirdUser  = User.objects.get(pk=5) 
        self.proposal   = Proposal.objects.get(pk=1)
        
    def testUserJoinToTeachers(self):
        self.proposal.addUserToTeachers(self.firstUser)
        self.assertEqual(self.proposal.teachers.count(), 1)

    def testUsersJoinToTeachers(self):
        self.proposal.addUserToTeachers(self.firstUser)
        self.proposal.addUserToTeachers(self.secondUser)
        self.assertEqual(self.proposal.teachers.count(), 2)

    def testUserStopBeTeacher1(self):
        self.proposal.addUserToTeachers(self.firstUser)
        self.proposal.deleteUserFromTeachers(self.firstUser)
        self.assertEqual(self.proposal.teachers.count(), 0)

    def testUserStopBeTeacher2(self):
        self.proposal.addUserToTeachers(self.firstUser)
        self.proposal.addUserToTeachers(self.secondUser)
        self.proposal.deleteUserFromTeachers(self.firstUser)
        self.assertEqual(self.proposal.teachers.count(), 1)

    def testUserIsntTeacher(self):
        self.assertRaises(NonEmployeeException, self.proposal.addUserToTeachers, self.thirdUser)

    def testUserIsntTeacher2(self):
        self.assertRaises(NonEmployeeException, self.proposal.deleteUserFromTeachers, self.thirdUser)
