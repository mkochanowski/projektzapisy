import random

from rest_framework import status
from django.urls import reverse

from apps.users.models import BaseUser
from ..models import Thesis
from .base import ThesesBaseTestCase, PAGE_SIZE


class ThesesListingTestCase(ThesesBaseTestCase):
    """Tests theses listing functionality: is the limit setting respected,
    are permissions granted correctly"""
    @classmethod
    def setUpTestData(cls):
        super(ThesesListingTestCase, cls).setUpTestData()
        cls.create_theses()

    @classmethod
    def create_theses(cls):
        cls.num_theses = random.randint(PAGE_SIZE, PAGE_SIZE * 2)
        theses = [cls.make_thesis() for _ in range(cls.num_theses)]
        Thesis.objects.bulk_create(theses)

    def _check_theses_response_data(self, data):
        self.assertTrue(isinstance(data, dict))
        self.assertTrue("count" in data)
        self.assertTrue("results" in data)
        results = data["results"]
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), PAGE_SIZE)

    def _test_user_can_list_theses(self, user: BaseUser):
        self.login_as(user)
        response = self.get_response_with_data()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_theses_response_data(response.data)

    def test_logged_in_can_list_theses(self):
        self._test_user_can_list_theses(self.get_random_student())
        self._test_user_can_list_theses(self.get_random_emp())
        self._test_user_can_list_theses(self.get_random_board_member())
        self._test_user_can_list_theses(self.get_admin())

    def test_logged_out_cannot_list_theses(self):
        response = self.client.get(reverse("theses:theses-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
