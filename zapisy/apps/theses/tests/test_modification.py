import random
from rest_framework import status
from django.urls import reverse

from ..models import Thesis, ThesisStatus, ThesisKind
from ..views import ThesisTypeFilter
from .base import ThesesBaseTestCase, PAGE_SIZE
from .factory_utils import random_vote


class ThesesModificationTestCase(ThesesBaseTestCase):
    def setUp(self):
        self.advisor = self.get_random_emp()
        self.thesis = self.make_thesis(advisor=self.advisor, status=ThesisStatus.being_evaluated)
        self.thesis.save()

    def update_thesis_with_data(self, data):
        return self.client.patch(
            f'{reverse("theses:theses-list")}{self.thesis.pk}/',
            data, format="json"
        )

    def test_student_cannot_modify_thesis(self):
        """Ensure that students are not permitted to modify theses"""
        student = self.get_random_student()
        self.login_as(student)
        new_reserved = not self.thesis.reserved
        response = self.update_thesis_with_data({"reserved": new_reserved})
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        modified_thesis = self.get_theses_with_data()[0]
        self.assertEqual(modified_thesis["reserved"], self.thesis.reserved)

    def test_emp_can_modify_their_thesis(self):
        """Ensure an employee can modify their own thesis, including changing the title
        because the thesis is still being evaluated"""
        self.login_as(self.advisor)
        new_title = "Some new title"
        new_desc = "Another description"
        new_student = self.get_random_student()
        response = self.update_thesis_with_data(
            {"title": new_title, "description": new_desc, "student": {"id": new_student.pk}}
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        modified_thesis = self.get_theses_with_data()[0]
        self.assertEqual(modified_thesis["title"], new_title)
        self.assertEqual(modified_thesis["description"], new_desc)
        self.assertEqual(modified_thesis["student"]["id"], new_student.pk)

    def _try_modify_accepted_title(self, new_title):
        self.thesis.status = ThesisStatus.accepted.value
        self.thesis.save()
        return self.update_thesis_with_data({"title": new_title})

    def test_emp_cannot_modify_their_accepted_thesis_title(self):
        """Ensure an employee cannot modify their thesis title if it's been accepted"""
        self.login_as(self.advisor)
        new_title = "A new title"
        response = self._try_modify_accepted_title(new_title)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        modified_thesis = self.get_theses_with_data()[0]
        self.assertNotEqual(modified_thesis["title"], new_title)

    def test_emp_can_modify_their_accepted_thesis_other_than_title(self):
        """Ensure that modifying things other than title is permitted"""
        self.thesis.status = ThesisStatus.accepted.value
        self.thesis.save()
        self.login_as(self.advisor)
        new_2nd_student = self.get_random_student()
        response = self.update_thesis_with_data({"student_2": {"id": new_2nd_student.pk}})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        modified_thesis = self.get_theses_with_data()[0]
        self.assertEqual(modified_thesis["student_2"]["id"], new_2nd_student.pk)

    def test_emp_cannot_modify_someone_elses_thesis(self):
        """Ensure that an employee cannot modify someone else's thesis"""
        another_emp = self.get_random_emp_different_from(self.advisor)
        self.login_as(another_emp)
        new_desc = "Another description"
        response = self.update_thesis_with_data({"description": new_desc})
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        modified_thesis = self.get_theses_with_data()[0]
        self.assertNotEqual(modified_thesis["description"], new_desc)

    def test_board_member_can_modify_accepted_title(self):
        """Ensure that board members are allowed to modify the title even if it's been accepted"""
        board_member = self.get_random_board_member()
        self.login_as(board_member)
        new_title = "A new title"
        response = self._try_modify_accepted_title(new_title)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        modified_thesis = self.get_theses_with_data()[0]
        self.assertEqual(modified_thesis["title"], new_title)

    def employee_cannot_vote(self):
        """Ensure that employees are not permitted to vote"""
        self.login_as(self.advisor)
        response = self.update_thesis_with_data({self.advisor.pk: random_vote().value})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)