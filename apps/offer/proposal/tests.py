# -*- coding:utf-8 -*-
"""
    Testy do propozycji przedmiotow
"""
from django.test import TestCase
from django.contrib.auth.models import User
from apps.offer.proposal.models import Proposal, ProposalDescription
from apps.offer.proposal.exceptions import NonStudentException, NonEmployeeException

class ProposalFansTest(TestCase):
    """
      Testy sprawdzajace poprawnosc popierania propozycji
    """
    fixtures = ['proposal_testing_users.json', 'proposal_testing.json']
    
    def setUp(self):
        """
           Konfiguracja
        """
        self.first_user  = User.objects.get(pk=5)
        self.second_user = User.objects.get(pk=6)
        self.third_user  = User.objects.get(pk=3) 
        self.proposall = Proposal.objects.get( name='Kurs 1' )

    def test_user_join_to_fans(self):
        """
           Uzystkownik wcisnal "popieram"
        """
        self.proposall.add_user_to_group(self.first_user, 'fans')
        self.assertEqual(self.proposall.fans.count(), 1)

    def test_users_join_to_fans(self):
        """
           Test na kilku uzytkownikach
        """
        self.proposall.add_user_to_group(self.first_user, 'fans')
        self.proposall.add_user_to_group(self.second_user, 'fans')
        self.assertEqual(self.proposall.fans.count(), 2)

    def test_user_stop_be_fan1(self):
        """
           user przestaje popierac
        """
        self.proposall.add_user_to_group(self.first_user, 'fans')
        self.proposall.delete_user_from_group(self.first_user, 'fans')
        self.assertEqual(self.proposall.fans.all().count(), 0)

    def test_user_stop_be_fan2(self):
        """
           user przestaje popierac
        """
        self.proposall.add_user_to_group(self.first_user, 'fans')
        self.proposall.add_user_to_group(self.second_user, 'fans')
        self.proposall.delete_user_from_group(self.first_user, 'fans')
        self.assertEqual(self.proposall.fans.all().count(), 1)

# sprawdzanie uprawnien:
    def test_user_isnt_fan(self):
        """
           Brak uprawnien
        """
        self.assertRaises(NonStudentException, self.proposall.add_user_to_group, self.third_user, 'fans')
    def test_user_isnt_fan2(self):
        self.assertRaises(NonStudentException, self.proposall.add_user_to_group, self.third_user, 'fans')
        
class ProposalhelpersTest(TestCase):
    """
	Test pomagajacych prowadzic
    """
    fixtures = ['proposal_testing_users.json', 'proposal_testing.json']
    
    def setUp(self):
        """
           Przygotowanie danych
        """
        self.first_user  = User.objects.get(pk=4)
        self.second_user = User.objects.get(pk=3)
        self.third_user  = User.objects.get(pk=5) 
        self.proposal   = Proposal.objects.get(pk=1)
        
    def test_user_join_to_helpers(self):
        """
          Testy
        """
        self.proposal.add_user_to_group(self.first_user, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 1)

    def test_users_join_to_helpers(self):
        """
          Testy
        """
        self.proposal.add_user_to_group(self.first_user, 'helpers')
        self.proposal.add_user_to_group(self.second_user, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 2)

    def test_user_stop_be_helpers1(self):
        """
           Testy
        """
        self.proposal.add_user_to_group(self.first_user, 'helpers')
        self.proposal.delete_user_from_group(self.first_user, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 0)

    def test_user_stop_be_helper2(self):
        """
           Testy
        """
        self.proposal.add_user_to_group(self.first_user, 'helpers')
        self.proposal.add_user_to_group(self.second_user, 'helpers')
        self.proposal.delete_user_from_group(self.first_user, 'helpers')
        self.assertEqual(self.proposal.helpers.count(), 1)

    def test_user_isnt_helper(self):
        """
           Testy
        """
        self.assertRaises(NonEmployeeException, self.proposal.add_user_to_group, self.third_user, 'helpers')

    def testUserIsntTeacher2(self):
        self.assertRaises(NonEmployeeException, self.proposal.delete_user_from_group, self.third_user, 'helpers')

class ProposalTeachersTest(TestCase):
    """
       Testy wykladowcow
    """
    fixtures = ['proposal_testing_users.json', 'proposal_testing.json']
    
    def setUp(self):
        """
           konfiguracja
        """
        self.first_user  = User.objects.get(pk=4)
        self.second_user = User.objects.get(pk=3)
        self.third_user  = User.objects.get(pk=5) 
        self.proposal   = Proposal.objects.get(pk=1)
        
    def test_user_join_to_teeachers(self):
        """
          Testy
        """
        self.proposal.add_user_to_group(self.first_user, 'teachers')
        self.assertEqual(self.proposal.teachers.count(), 1)

    def test_users_join_to_teachers(self):
        """
          Testy
        """
        self.proposal.add_user_to_group(self.first_user, 'teachers')
        self.proposal.add_user_to_group(self.second_user, 'teachers')
        self.assertEqual(self.proposal.teachers.count(), 2)

    def test_user_stop_be_teacher1(self):
        """
          Testy
        """
        self.proposal.add_user_to_group(self.first_user, 'teachers')
        self.proposal.delete_user_from_group(self.first_user, 'teachers')
        self.assertEqual(self.proposal.teachers.count(), 0)

    def test_user_stop_be_teacher2(self):
        """
          Testy
        """
        self.proposal.add_user_to_group(self.first_user, 'teachers')
        self.proposal.add_user_to_group(self.second_user, 'teachers')
        self.proposal.delete_user_from_group(self.first_user, 'teachers')
        self.assertEqual(self.proposal.teachers.count(), 1)

    def test_user_isnt_employee(self):
        """
           Testy
        """
        self.assertRaises(NonEmployeeException, self.proposal.add_user_to_group, self.third_user, 'teachers')

    def test_user_isnt_employee(self):
        """
           Testy
        """
        self.assertRaises(NonEmployeeException, self.proposal.delete_user_from_group, self.third_user, 'teachers')


