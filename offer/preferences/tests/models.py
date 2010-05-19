# -*- coding:utf-8 -*-

from django.test import TestCase
from offer.proposal.models import Proposal
from offer.preferences.exceptions import *
from offer.preferences.models import Preference
from users.models import Employee

class PreferenceModelClassTest(TestCase):
    fixtures = ['three_employees.json', 
                'preferences_testing_data.json']
    
    def setUp(self):
        self.emp = Employee.objects.get(user__username='emp2')
        course1 = Proposal.objects.get(name='Kurs 1')
        course2 = Proposal.objects.get(name='Kurs 2')
        self.hidden = Preference.objects.get(employee=self.emp,
                                              proposal=course2)
        self.shown  = Preference.objects.get(employee=self.emp,
                                              proposal=course1)
    
    def test_hide_on_shown(self):
        self.shown.hide()
        self.assertEquals(self.shown.hidden,  True)
        
    def test_unhide_on_hidden(self):
        self.hidden.unhide()
        self.assertEquals(self.hidden.hidden, False)
        
    def test_set_preference(self):
        self.hidden.set_preference(lecture=3, review_lecture=3)
        self.assertEquals(self.hidden.lecture,        3)
        self.assertEquals(self.hidden.review_lecture, 3)        
        self.assertEquals(self.hidden.tutorial,       0)
        self.assertEquals(self.hidden.lab,            0)
        self.hidden.set_preference(tutorial=2, lab=2)
        self.assertEquals(self.hidden.tutorial, 2)
        self.assertEquals(self.hidden.lab,      2)        
    
    def test_set_preference_to_unknown_value(self):
        self.assertRaises(UnknownPreferenceValue, 
                          self.hidden.set_preference, 
                          lab=5)
    
class PreferenceManagerGettersTest(TestCase):
    fixtures = ['three_employees.json', 
                'preferences_testing_data.json']

    def setUp(self):
        self.emp1 = Employee.objects.get(user__username='emp1')
        self.emp2 = Employee.objects.get(user__username='emp2')
        self.emp3 = Employee.objects.get(user__username='emp3')
        self.course1 = Proposal.objects.get(name='Kurs 1')
        self.course2 = Proposal.objects.get(name='Kurs 2')
        self.seminar = Proposal.objects.get(name='Seminarium 1')
    
    def assertProps(self, prefs, expected):
        given = set([p.proposal for p in prefs])
        self.assertEquals(given, set(expected))
    
    def test_get_employees_prefs(self):
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp1),
            [])
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2),
            [self.course1, self.seminar])
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp3),
            [self.course1])
    
    def test_get_set_with_hidden(self):
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp1, hidden=True),
            [])
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2, hidden=True),
            [self.course1, self.course2, self.seminar])
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp3, hidden=True),
            [self.course1])
    
    def test_get_set_by_type(self):
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2, types=['seminar']),
            [self.seminar])
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2, types=['cs_1']),
            [self.course1])
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2, types=['cs_1','seminar']),
            [self.seminar, self.course1])
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2,
                                                   hidden=True,
                                                   types=['cs_2']),
            [self.course2])
    
    def test_get_set_filtered_without_hidden(self):
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2, query='kurs'),
            [self.course1])
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2, query='semi'),
            [self.seminar])
    
    def test_get_set_filtered_with_hidden(self):
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2, hidden=True, query='kurs'),
            [self.course1, self.course2])
        self.assertProps(
            Preference.objects.get_employees_prefs(self.emp2, hidden=True, query='semi'),
            [self.seminar])
    
    def test_init_preference_already_set(self):
        self.assertRaises(CoursePreferencesAlreadySet, 
                          Preference.objects.init_preference,
                          self.emp3,
                          self.course1)
    
    def test_init_preference_not_set(self):
        Preference.objects.init_preference(self.emp3, self.seminar)
        self.assertProps(Preference.objects.get_employees_prefs(self.emp3),
                         [self.course1, self.seminar])
    
    def test_init_preference_initial_values(self):
        Preference.objects.init_preference(self.emp3, self.seminar)
        try:
            pref = Preference.objects.get(employee=self.emp3, proposal=self.seminar)
        except Preference.DoesNotExist:
            self.fail("Failed to create expected Preference.")
        self.assertEquals(pref.lecture,        0)
        self.assertEquals(pref.review_lecture, 0)
        self.assertEquals(pref.tutorial,       0)
        self.assertEquals(pref.lab,            0)
