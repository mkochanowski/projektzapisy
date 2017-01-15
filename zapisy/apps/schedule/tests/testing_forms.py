# -*- coding: utf-8 -*-

from django.test import TestCase

from ..forms import EventForm
from apps.users.tests.factories import EmployeeFactory, StudentFactory, UserProfileFactory
from ..models.event import Event


class EventFormTestCase(TestCase):
    def test_event_form_accepts_blank_description_when_user_is_employee(self):
        e = EmployeeFactory()
        UserProfileFactory(user=e.user, is_employee=True)
        data = {'description': ''}
        form = EventForm(e.user, data)
        self.assertTrue(form.is_valid())

    def test_event_form_accepts_blank_description_when_user_is_student(self):
        pass
        # s = StudentFactory()
        # UserProfileFactory(user=s.user, is_student=True)
        # s.user.employee = None
        # event_form = EventForm(s.user)
