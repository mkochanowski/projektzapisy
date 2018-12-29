from rest_framework import status
from django.urls import reverse

from apps.users.models import Employee, BaseUser

from ..models import ThesisStatus, ThesisVote
from ..system_settings import get_num_required_votes
from .base import ThesesBaseTestCase
from .factory_utils import random_vote


class ThesesModificationTestCase(ThesesBaseTestCase):
    """Tests that theses modification via the REST API (PATCH requests)
    and related processing work correctly
    """
    def setUp(self):
        self.advisor = self.get_random_emp()
        self.thesis = self.make_thesis(advisor=self.advisor, status=ThesisStatus.being_evaluated)
        self.thesis.save()

    def update_thesis_with_data(self, data):
        return self.client.patch(
            f'{reverse("theses:theses-list")}{self.thesis.pk}/',
            data, format="json"
        )

    def get_modified_thesis(self):
        """Re-fetch the thesis we're modifying from the backend code
        There will always be only one instance as we create just one in setUp
        """
        return self.get_theses_with_data()[0]

    def test_student_cannot_modify_thesis(self):
        """Ensure that students are not permitted to modify theses"""
        student = self.get_random_student()
        self.login_as(student)
        new_reserved = not self.thesis.reserved
        response = self.update_thesis_with_data({"reserved": new_reserved})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        modified_thesis = self.get_modified_thesis()
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        modified_thesis = self.get_modified_thesis()
        self.assertEqual(modified_thesis["title"], new_title)
        self.assertEqual(modified_thesis["description"], new_desc)
        self.assertEqual(modified_thesis["student"]["id"], new_student.pk)

    FROZEN_STATUSES = [
        ThesisStatus.accepted,
        ThesisStatus.in_progress,
        ThesisStatus.defended,
    ]

    def _try_modify_frozen_with_data(self, data):
        result = []
        for frozen_status in ThesesModificationTestCase.FROZEN_STATUSES:
            self.thesis.status = frozen_status.value
            self.thesis.save()
            result.append(self.update_thesis_with_data(data))
        return result

    def test_emp_cannot_modify_their_frozen_thesis_title(self):
        """Ensure an employee cannot modify their thesis title if it's been "frozen" """
        self.login_as(self.advisor)
        new_title = "A new title"
        responses = self._try_modify_frozen_with_data({"title": new_title})
        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        modified_thesis = self.get_modified_thesis()
        self.assertNotEqual(modified_thesis["title"], new_title)

    def test_emp_can_modify_their_frozen_thesis_other_than_title(self):
        """Ensure that modifying things other than title is permitted"""
        self.login_as(self.advisor)
        new_2nd_student = self.get_random_student()
        responses = self._try_modify_frozen_with_data({"student_2": {"id": new_2nd_student.pk}})
        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        modified_thesis = self.get_modified_thesis()
        self.assertEqual(modified_thesis["student_2"]["id"], new_2nd_student.pk)

    def test_emp_cannot_modify_someone_elses_thesis(self):
        """Ensure that an employee cannot modify someone else's thesis"""
        another_emp = self.get_random_emp_different_from(self.advisor)
        self.login_as(another_emp)
        new_desc = "Another description"
        response = self.update_thesis_with_data({"description": new_desc})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        modified_thesis = self.get_modified_thesis()
        self.assertNotEqual(modified_thesis["description"], new_desc)

    def test_board_member_can_modify_frozen_title(self):
        """Ensure that board members are allowed to modify the title even if it's been "frozen" """
        board_member = self.get_random_board_member()
        self.login_as(board_member)
        new_title = "A new title"
        responses = self._try_modify_frozen_with_data({"title": new_title})
        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        modified_thesis = self.get_modified_thesis()
        self.assertEqual(modified_thesis["title"], new_title)

    def cast_vote_as(self, voter: Employee, vote: ThesisVote):
        return self.update_thesis_with_data({"votes": {voter.pk: vote.value}})

    def test_student_cannot_vote(self):
        """Ensure that students are not permitted to vote"""
        student = self.get_random_student()
        self.login_as(student)
        board_member = self.get_random_board_member()
        response = self.cast_vote_as(board_member, random_vote())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_vote(self):
        """Ensure that employees are not permitted to vote"""
        self.login_as(self.advisor)
        board_member = self.get_random_board_member()
        response = self.cast_vote_as(board_member, random_vote())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_board_members_can_vote_as_themselves(self):
        """Ensure board members can vote, but only as themselves"""
        board_member = self.get_random_board_member()
        self.login_as(board_member)
        response = self.cast_vote_as(board_member, random_vote())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_board_members_cannot_vote_as_other(self):
        """Ensure board members cannot vote as anyone else"""
        board_member = self.get_random_board_member_different_from(self.get_admin())
        another_member = self.get_random_board_member_different_from(board_member)
        self.login_as(board_member)
        response = self.cast_vote_as(another_member, random_vote())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_vote_as_anyone(self):
        """Ensure the system admin can cast votes as any board member"""
        admin = self.get_admin()
        another_member = self.get_random_board_member_different_from(admin)
        self.login_as(admin)
        response = self.cast_vote_as(another_member, random_vote())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_cannot_cast_vote_as_non_board_member(self):
        """Ensure that even the admin cannot vote as someone
        who isn't a member of the theses board"""
        admin = self.get_admin()
        emp = self.get_random_emp()
        self.login_as(admin)
        response = self.cast_vote_as(emp, random_vote())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def vote_to_accept_thesis_required_times(self, voter_to_skip: Employee = None):
        """Cast enough approving votes to accept the current thesis, not using
        the specified voter (if specified)
        """
        num_required = get_num_required_votes()
        self.assertLessEqual(num_required, len(self.board_members))
        voters = []
        while len(voters) < num_required:
            voter = self.get_random_board_member_different_from(voter_to_skip)
            while voter in voters:
                voter = self.get_random_board_member_different_from(voter_to_skip)
            voters.append(voter)
        for voter in voters:
            self.login_as(voter)
            response = self.cast_vote_as(voter, ThesisVote.accepted)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enough_votes_accept_thesis(self):
        """Test that when enough board members vote "approve" on a thesis, it gets accepted"""
        self.vote_to_accept_thesis_required_times()
        modified_thesis = self.get_modified_thesis()
        self.assertEqual(modified_thesis["status"], ThesisStatus.accepted.value)

    def reject_thesis_once(self, voter: Employee):
        """Cast a rejecting vote for the current thesis as the given voter"""
        self.login_as(voter)
        response = self.cast_vote_as(voter, ThesisVote.rejected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_single_rejection_rejects_thesis(self):
        """Ensure that a single rejection is enough to reject a thesis"""
        self.reject_thesis_once(self.get_random_board_member())
        modified_thesis = self.get_modified_thesis()
        self.assertEqual(modified_thesis["status"], ThesisStatus.returned_for_corrections.value)

    def test_enough_votes_dont_accept_after_rejection(self):
        """Ensure that if a thesis was rejected, it will not be accepted again even if
        enough "approve" votes are cast
        """
        rejecter = self.get_random_board_member()
        self.reject_thesis_once(rejecter)
        self.vote_to_accept_thesis_required_times(rejecter)
        modified_thesis = self.get_modified_thesis()
        self.assertEqual(modified_thesis["status"], ThesisStatus.returned_for_corrections.value)

    def _test_cannot_modify_thesis_duplicate_title_as_user(self, user: BaseUser):
        other_thesis = self.make_thesis()
        other_thesis.save()
        padded_title = '\n\t   {other_thesis.title}   \t\t\n       '
        self.login_as(user)
        response = self.update_thesis_with_data({"title": padded_title})
        self.assertTrue(response.status_code, status.HTTP_409_CONFLICT)

    def test_cannot_modify_thesis_duplicate_title(self):
        """Test that a thesis cannot be modified to contain a duplicate title by any user"""
        self._test_cannot_modify_thesis_duplicate_title_as_user(self.advisor)
        self._test_cannot_modify_thesis_duplicate_title_as_user(
            self.get_random_board_member_not_admin()
        )
        self._test_cannot_modify_thesis_duplicate_title_as_user(self.get_admin())
