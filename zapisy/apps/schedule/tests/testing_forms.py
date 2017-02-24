# -*- coding: utf-8 -*-

from django.test import TestCase

from ..forms import EventForm
from apps.enrollment.courses.tests.objectmothers import ClassroomObjectMother
from apps.users.tests.factories import UserProfileFactory, UserFactory, EmployeeFactory
from apps.enrollment.courses.models import Classroom


class EventFormTestCase(TestCase):
    def setUp(self):
        room110 = ClassroomObjectMother.room110()
        room110.save()

    def test_event_form_accepts_blank_description_when_user_is_employee(self):
        e = EmployeeFactory()
        UserProfileFactory(user=e.user, is_employee=True)
        data = {'description': ''}
        form = EventForm(e.user, data)
        self.assertTrue(form.is_valid())

    def test_event_form_accepts_blank_description_when_user_is_student(self):
        user = UserFactory()
        UserProfileFactory(user=user, is_student=True, is_employee=False)
        data = {'description': ''}
        form = EventForm(user, data)
        self.assertTrue(form.is_valid())
