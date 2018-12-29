from typing import List
import json
import random

from rest_framework import status
from django.urls import reverse

from apps.users.models import Employee, BaseUser

from ..models import ThesisStatus, ThesisVote
from ..users import ThesisUserType
from ..system_settings import get_num_required_votes
from .base import ThesesBaseTestCase
from .factory_utils import random_definite_vote, make_employee_with_name, make_student_with_name


class OtherEndpointsTestCase(ThesesBaseTestCase):
    """Tests remaining endpoints - current user, num ungraded, autocomplete etc"""

    def test_theses_board_denied_for_not_logged_in(self):
        """Ensure that unauthenticated users are not permitted to query about the theses board"""
        response = self.client.get(reverse("theses:theses_board-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_theses_board_ok_for_user(self, user: BaseUser):
        """Ensure the specified user can access the theses board and gets correct results"""
        self.login_as(user)
        response = self.client.get(reverse("theses:theses_board-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertEqual(len(self.board_members), len(data))
        for member in self.board_members:
            self.assertTrue(any(recvd_member["id"] == member.pk for recvd_member in data))

    def test_theses_board_ok_for_logged_in(self):
        """Ensure that logged in users of various types can access the theses board"""
        self._test_theses_board_ok_for_user(self.get_random_emp())
        self._test_theses_board_ok_for_user(self.get_random_student())
        self._test_theses_board_ok_for_user(self.get_random_board_member())

    def test_current_user_endpoint_denied_for_logged_in(self):
        """Ensure that unauthenticated users cannot access the current user endpoint"""
        response = self.client.get(reverse("theses:current_user"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_current_user_for_user(self, user: BaseUser, expected_type: ThesisUserType):
        self.login_as(user)
        response = self.client.get(reverse("theses:current_user"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["type"], expected_type.value)
        self.assertEqual(data["user"]["id"], user.pk)
        self.assertEqual(data["user"]["display_name"], user.get_full_name())

    def test_current_user_endpoint_ok_for_logged_in(self):
        """Ensure the current user endpoint returns correct data for each possible
        type of user
        """
        self._test_current_user_for_user(self.get_admin(), ThesisUserType.admin)
        self._test_current_user_for_user(self.get_random_emp(), ThesisUserType.employee)
        self._test_current_user_for_user(self.get_random_student(), ThesisUserType.student)

    def test_autocomplete_denied_for_not_logged_in(self):
        """Ensure users that are not logged in cannot access the student/emp
        autocomplete endpoint. This is important as these endpoints return
        lists containing both names and user IDs
        """
        response = self.client.get(reverse("theses:student-autocomplete"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(reverse("theses:employee-autocomplete"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_autocomplete_filtering(
        self, url: str, matching_users: List[BaseUser], search_filter: str
    ):
        response = self.client.get(url, {"q": search_filter})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        results = data["results"]
        self.assertEqual(len(results), len(matching_users))
        for matching_user in matching_users:
            self.assertTrue(any(
                int(recvd_user["id"]) == matching_user.pk and
                recvd_user["text"] == matching_user.get_full_name()
                for recvd_user in results)
            )

    def test_autocomplete_allowed_and_filtered_for_logged_in(self):
        """Ensure logged in users can download the autocomplete list
        and that it's correctly filtered
        """
        emp = self.get_random_emp()
        self.login_as(emp)

        matching_emp_names = ["abc", "abces"]
        nonmatching_emp_names = ["abdec", "xyz"]
        matching_emps = [make_employee_with_name(name) for name in matching_emp_names]
        for name in nonmatching_emp_names:
            make_employee_with_name(name)
        self._test_autocomplete_filtering(
            reverse("theses:employee-autocomplete"), matching_emps, "abc"
        )

        matching_stud_names = ["foo", "foobar"]
        nonmatching_stud__names = ["other", "quux"]
        matching_emps = [make_student_with_name(name) for name in matching_stud_names]
        for name in nonmatching_stud__names:
            make_student_with_name(name)
        self._test_autocomplete_filtering(
            reverse("theses:student-autocomplete"), matching_emps, "foo"
        )

    def test_num_ungraded_denied_for_not_logged_in(self):
        """Ensure that unauthenticated users cannot access the num ungraded endpoint"""
        response = self.client.get(reverse("theses:num_ungraded"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def get_num_ungraded_response_for_user(self, user: BaseUser) -> int:
        self.login_as(user)
        return self.client.get(reverse("theses:num_ungraded"))

    def test_num_ungraded_ok_for_board_member(self):
        """Ensure that the num ungraded endpoint works correctly for board members"""
        board_member = self.get_random_board_member()
        num_theses = random.randint(10, 20)
        theses = [self.make_thesis() for i in range(num_theses)]
        for thesis in theses:
            # This is needed since the thesis vote bindings created below need a pk
            # to reference
            thesis.save()
        num_graded = num_theses // 2
        graded_theses = random.sample(theses, num_graded)
        for graded in graded_theses:
            votes = [(board_member, random_definite_vote())]
            graded.process_new_votes(votes)
        response = self.get_num_ungraded_response_for_user(board_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, len(theses) - len(graded_theses))

    def test_num_ungraded_returns_404_for_non_board_member(self):
        """Ensure that if a user that isn't a board member makes a num ungraded request,
        they get a 404 error"""
        response = self.get_num_ungraded_response_for_user(self.get_random_emp())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.get_num_ungraded_response_for_user(self.get_random_student())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
