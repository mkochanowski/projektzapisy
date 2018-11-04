from django.test import TestCase

from apps.notifications2.exceptions import DescriptionArgumentMissingException
from apps.notifications2.utils import render_description


class Notifications2UtilsTestCase(TestCase):

    def test_fake_desc_renders_properly(self):
        descr_args = {'example_arg': 'to bedzie wklejone'}

        rendered = render_description('fake_desc', descr_args)

        self.assertEqual(
            'lorem ipsum dolor sit amet to bedzie wklejone zażółć gęślą jaźń',
            rendered)

    def test_trying_to_render_with_insufficient_arguments_raises(self):
        descr_args = {}

        with self.assertRaises(DescriptionArgumentMissingException):
            rendered = render_description('fake_desc', descr_args)
