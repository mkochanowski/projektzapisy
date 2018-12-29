from rest_framework import status
from django.urls import reverse

from apps.users.models import Employee, BaseUser
from ..models import ThesisStatus
from .factory_utils import random_title, random_kind, random_reserved
from .base import ThesesBaseTestCase


class ThesesAdditionTestCase(ThesesBaseTestCase):
    def add_thesis(self, adder: Employee, **kwargs):
        """Try to add a thesis with the specified params
        (or defaults if missing) as the specified user
        """
        self.login_as(adder)
        advisor = kwargs.pop("advisor", adder)
        base_data = {
            "title": random_title(),
            "advisor": {"id": advisor.pk},
            "kind": random_kind().value,
            "reserved": random_reserved(),
            "status": ThesisStatus.being_evaluated.value
        }
        base_data.update(kwargs)
        return self.client.post(reverse("theses:theses-list"), base_data, format="json")

    # Students can't add a thesis
    def test_student_cannot_add_thesis(self):
        stud = self.get_random_student()
        emp = self.get_random_emp()
        # Use a separate employee as the advisor to make sure the request
        # isn't rejected just because the advisor is invalid and actually
        # looks at the user sending it
        response = self.add_thesis(stud, advisor=emp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Regular employees cannot add a thesis with someone else as the advisor
    def test_employee_can_add_own_thesis(self):
        emp = self.get_random_emp()
        response = self.add_thesis(emp)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employee_cannot_add_someone_elses_thesis(self):
        emp = self.get_random_emp()
        other_emp = self.get_random_emp_different_from(emp)
        response = self.add_thesis(emp, advisor=other_emp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ...or with status set to anything other than being evaluated
    def test_employee_cannot_add_thesis_with_other_status(self):
        emp = self.get_random_emp()
        response = self.add_thesis(emp, status=ThesisStatus.accepted.value)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # But board members can
    def test_board_member_can_add_someone_elses_thesis(self):
        emp = self.get_random_board_member()
        other_emp = self.get_random_emp_different_from(emp)
        response = self.add_thesis(emp, advisor=other_emp)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_board_member_can_add_thesis_with_other_status(self):
        emp = self.get_random_board_member()
        response = self.add_thesis(emp, status=ThesisStatus.accepted.value)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Theses with empty titles are not permitted
    def ensure_user_cannot_add_thesis_with_empty_title(self, user):
        response = self.add_thesis(user, title="")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_add_thesis_with_empty_title(self):
        self.ensure_user_cannot_add_thesis_with_empty_title(self.get_random_emp())
        board_member = self.get_random_board_member_not_admin()
        self.ensure_user_cannot_add_thesis_with_empty_title(board_member)
        self.ensure_user_cannot_add_thesis_with_empty_title(self.get_admin())

    def ensure_409_with_user(self, user: BaseUser):
        title = random_title()
        thesis = self.make_thesis(title=title)
        thesis.save()
        # Padding at each end should be trimmed, so this is still a dupe
        padded_title = f'  \t{title}    \n   '
        response = self.add_thesis(user, title=padded_title)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # Titles must be unique, for all users
    def test_admin_cannot_add_thesis_with_duplicate_title(self):
        self.ensure_409_with_user(self.get_admin())

    def test_board_member_cannot_add_thesis_with_duplicate_title(self):
        self.ensure_409_with_user(self.get_random_board_member_different_from(self.get_admin()))

    def test_emp_cannot_add_thesis_with_duplicate_title(self):
        self.ensure_409_with_user(self.get_random_emp())
