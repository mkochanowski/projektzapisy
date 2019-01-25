from django.test import TestCase

from apps.notifications2.exceptions import DescriptionArgumentMissingException
from apps.notifications2.utils import render_description
from apps.notifications2.templates import (
    ADDED_NEW_GROUP,
    ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER,
    PULLED_FROM_QUEUE,
)


class Notifications2UtilsTestCase(TestCase):

    def test_pulled_from_queue_renders_properly(self):
        descr_args = {'course_name': 'matematyka dyskretna', 'teacher': 'Jan Kowalski', 'type': 'ćwiczenia'}

        rendered = render_description(PULLED_FROM_QUEUE, descr_args)

        self.assertEqual(
            'Nastąpiło wciągnięcie Cię do grupy przedmiotu matematyka dyskretna, gdzie prowadzący to Jan Kowalski a typ grupy ćwiczenia',
            rendered)

    def test_added_new_group_renders_properly(self):
        descr_args = {'course_name': 'matematyka dyskretna', 'teacher': 'Jan Kowalski'}

        rendered = render_description(ADDED_NEW_GROUP, descr_args)

        self.assertEqual(
            'W przedmiocie matematyka dyskretna została dodana grupa prowadzona przez Jan Kowalski',
            rendered)

    def test_assigned_to_new_group_as_teacher_renders_properly(self):
        descr_args = {'course_name': 'matematyka dyskretna'}

        rendered = render_description(ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER, descr_args)

        self.assertEqual(
            'Przydzielono Cię do grupy przedmiotu matematyka dyskretna jako prowadzącego',
            rendered)

    def test_trying_to_render_with_insufficient_arguments_raises(self):
        descr_args = {}

        with self.assertRaises(DescriptionArgumentMissingException):
            rendered = render_description(PULLED_FROM_QUEUE, descr_args)
