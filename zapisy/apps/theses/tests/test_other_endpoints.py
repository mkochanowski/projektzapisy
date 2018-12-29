from rest_framework import status
from django.urls import reverse

from apps.users.models import Employee, BaseUser

from ..models import ThesisStatus, ThesisVote
from ..users import ThesisUserType
from ..system_settings import get_num_required_votes
from .base import ThesesBaseTestCase
from .factory_utils import random_vote


class OtherEndpointsTestCase(ThesesBaseTestCase):
    """Tests remaining endpoints - current user, num ungraded, autocomplete etc"""
    def _test_current_user_for_user(self, user: BaseUser, expected_type: ThesisUserType):
        self.login_as(user)
        response = self.client.get(reverse("theses:current_user"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["type"], expected_type.value)
        self.assertEqual(data["user"]["id"], user.pk)
        self.assertEqual(data["user"]["display_name"], user.get_full_name())

    def test_current_user_endpoint(self):
        self._test_current_user_for_user(self.get_admin(), ThesisUserType.admin)
        self._test_current_user_for_user(self.get_random_emp(), ThesisUserType.employee)
        self._test_current_user_for_user(self.get_random_student(), ThesisUserType.student)

    def test_theses_board_endpoint(self):
        self.login_as(self.get_random_emp())
        response = self.client.get(reverse("theses:theses_board-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertEqual(len(self.board_members), len(data))
        for member in self.board_members:
            self.assertTrue(any(recvd_member["id"] == member.pk for recvd_member in data))