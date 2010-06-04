# -*- coding:utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Employee, Student
from offer.proposal.models import Proposal, ProposalDescription
from offer.proposal.exceptions import *

class ProposalFansTest(TestCase):
    fixtures = ['proposal_testing_users.json', 'proposal_testing.json']
    
    def setUp(self):
        self.firstUser  = User.objects.get(pk=5)
        self.secondUser = User.objects.get(pk=6)
        self.thirdUser  = User.objects.get(pk=3) 
        self.proposall = Proposal.objects.get( name='Kurs 1' )

    def testUserJoinToFans(self):
        self.proposall.add_user_to_group(self.firstUser, 'fans')
        self.assertEqual(self.proposall.fans.count(), 1)

    def testUsersJoinToFans(self):
        self.proposall.add_user_to_group(self.firstUser, 'fans')
        self.proposall.add_user_to_group(self.secondUser, 'fans')
        self.assertEqual(self.proposall.fans.count(), 2)

    def testUserStopBeFan1(self):
        self.proposall.add_user_to_group(self.firstUser, 'fans')
        self.proposall.delete_user_from_group(self.firstUser, 'fans')
        self.assertEqual(self.proposall.fans.all().count(), 0)

    def testUserStopBeFan2(self):
        self.proposall.add_user_to_group(self.firstUser, 'fans')
        self.proposall.add_user_to_group(self.secondUser, 'fans')
        self.proposall.delete_user_from_group(self.firstUser, 'fans')
        self.assertEqual(self.proposall.fans.all().count(), 1)

# sprawdzanie uprawnien:
    def testUserIsntFan(self):
        self.assertRaises(NonStudentException, self.proposall.add_user_to_group, self.thirdUser, 'fans')
    def testUserIsntFan2(self):
        self.assertRaises(NonStudentException, self.proposall.add_user_to_group, self.thirdUser, 'fans')
        
class ProposalhelpersTest(TestCase):
    fixtures = ['proposal_testing_users.json', 'proposal_testing.json']
    
    def setUp(self):
        self.firstUser  = User.objects.get(pk=4)
        self.secondUser = User.objects.get(pk=3)
        self.thirdUser  = User.objects.get(pk=5) 
        self.proposal   = Proposal.objects.get(pk=1)
        
    def testUserJoinTohelpers(self):
        self.proposal.add_user_to_group(self.firstUser, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 1)

    def testUsersJoinTohelpers(self):
        self.proposal.add_user_to_group(self.firstUser, 'helpers')
        self.proposal.add_user_to_group(self.secondUser, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 2)

    def testUserStopBeTeacher1(self):
        self.proposal.add_user_to_group(self.firstUser, 'helpers')
        self.proposal.delete_user_from_group(self.firstUser, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 0)

    def testUserStopBeTeacher2(self):
        self.proposal.add_user_to_group(self.firstUser, 'helpers')
        self.proposal.add_user_to_group(self.secondUser, 'helpers')
        self.proposal.delete_user_from_group(self.firstUser, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 1)

    def testUserIsntTeacher(self):
        self.assertRaises(NonEmployeeException, self.proposal.add_user_to_group, self.thirdUser, 'helpers')

    def testUserIsntTeacher2(self):
        self.assertRaises(NonEmployeeException, self.proposal.delete_user_from_group, self.thirdUser, 'helpers')

class ProposalHelpersTest(TestCase):
    fixtures = ['proposal_testing_users.json', 'proposal_testing.json']
    
    def setUp(self):
        self.firstUser  = User.objects.get(pk=4)
        self.secondUser = User.objects.get(pk=3)
        self.thirdUser  = User.objects.get(pk=5) 
        self.proposal   = Proposal.objects.get(pk=1)
        
    def testUserJoinToHelpers(self):
        self.proposal.add_user_to_group(self.firstUser, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 1)

    def testUsersJoinToHelpers(self):
        self.proposal.add_user_to_group(self.firstUser, 'helpers')
        self.proposal.add_user_to_group(self.secondUser, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 2)

    def testUserStopBeHepler1(self):
        self.proposal.add_user_to_group(self.firstUser, 'helpers')
        self.proposal.delete_user_from_group(self.firstUser, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 0)

    def testUserStopBeHepler2(self):
        self.proposal.add_user_to_group(self.firstUser, 'helpers')
        self.proposal.add_user_to_group(self.secondUser, 'helpers')
        self.proposal.delete_user_from_group(self.firstUser, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 1)

    def testUserIsntEmployee(self):
        self.assertRaises(NonEmployeeException, self.proposal.add_user_to_group, self.thirdUser, 'helpers')

    def testUserIsntEmployee(self):
        self.assertRaises(NonEmployeeException, self.proposal.delete_user_from_group, self.thirdUser, 'helpers')


class ProposalTaggingTest(TestCase):
    fixtures = ['proposal_testing_users.json', 'proposal_testing.json']

    def setUp(self):
        self.proposal    = Proposal.objects.get(pk=1)
        self.description = ProposalDescription.objects.get(pk=1)

    def testTagProposalWithExistingTag(self):
        self.proposal.add_tag("sampletag")
        self.assertTrue(self.proposal
                        in Proposal.get_by_tag("sampletag"))
    
    def testTagProposalWithNonexistentTag(self):
        self.proposal.add_tag("othertag")
        self.assertTrue(self.proposal
                        in Proposal.get_by_tag("othertag"))       
    
    def testTagProposalDescriptionWithExistingTag(self):
        self.description.add_tag("sampletag")
        self.assertTrue(self.description
                        in ProposalDescription.get_by_tag("sampletag"))
    
    def testTagProposalDescriptionWithNonexistentTag(self):
        self.description.add_tag("othertag")
        self.assertTrue(self.description
                        in ProposalDescription.get_by_tag("othertag"))
    
    def testUntagProposal(self):
        self.proposal.remove_tag("default")
        self.assertFalse(self.proposal
                         in Proposal.get_by_tag("default"))
    
    def testUntagProposalDescription(self):
        self.description.remove_tag("default")
        self.assertFalse(self.description
                         in ProposalDescription.get_by_tag("default"))
