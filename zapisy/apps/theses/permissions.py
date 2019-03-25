"""This module defines high-level thesis-related permissions
checks used when deserializing a received thesis object and performing actions.
"""
from typing import Optional

from apps.users.models import Employee, BaseUser

from .models import Thesis, ThesisStatus, UNVOTEABLE_STATUSES
from .users import (
    ThesisUserType, get_user_type, is_theses_board_member,
    is_admin, is_regular_employee, is_master_rejecter,
)


def is_thesis_staff(user: BaseUser) -> bool:
    """Determine whether the user should be considered a "staff member" in the theses system"""
    return is_admin(user) or is_theses_board_member(user)


def can_add_thesis(user: BaseUser) -> bool:
    """Is the given user permitted to add new thesis objects?"""
    user_type = get_user_type(user)
    return user_type != ThesisUserType.STUDENT


def is_owner_of_thesis(user: BaseUser, thesis: Thesis) -> bool:
    """Is the specified user the advisor of the specified thesis?"""
    return thesis.advisor == user


EMPLOYEE_DELETABLE_STATUSES = (
    ThesisStatus.BEING_EVALUATED,
    ThesisStatus.RETURNED_FOR_CORRECTIONS
)


def can_delete_thesis(user: BaseUser, thesis: Thesis) -> bool:
    """Determine if the specified user is permitted to delete the specified thesis"""
    return (
        is_admin(user) or
        is_theses_board_member(user) and not thesis.is_archived() or
        is_regular_employee(user) and is_owner_of_thesis(user, thesis) and
        ThesisStatus(thesis.status) in EMPLOYEE_DELETABLE_STATUSES
    )


def can_modify_thesis(user: BaseUser, thesis: Thesis) -> bool:
    """Is the specified user permitted to make any changes to the specified thesis?"""
    if thesis.is_archived():
        return is_admin(user)
    return is_thesis_staff(user) or is_owner_of_thesis(user, thesis)


"""The detailed checks below will only be performed
if it is determined that the user is permitted to modify the thesis in general,
so there's no need to check that again
"""


def can_change_title(user: BaseUser, thesis: Thesis) -> bool:
    """Is the specified user permitted to change the title of the specified thesis?"""
    allowed_statuses = (ThesisStatus.BEING_EVALUATED, ThesisStatus.RETURNED_FOR_CORRECTIONS)
    return (
        is_thesis_staff(user) or
        is_owner_of_thesis(user, thesis) and ThesisStatus(thesis.status) in allowed_statuses
    )


def can_set_status_for_new(user: BaseUser, status: ThesisStatus) -> bool:
    """Can the specified user set the specified status for a new thesis?"""
    return is_thesis_staff(user) or status == ThesisStatus.BEING_EVALUATED


def can_change_status_to(user: BaseUser, thesis: Thesis, new_status: ThesisStatus) -> bool:
    """Can the specified user change the status
    of the specified thesis to the new specified status?"""
    old_status = ThesisStatus(thesis.status)
    return (
        is_admin(user) or
        is_master_rejecter(user) or
        is_theses_board_member(user) and new_status != ThesisStatus.RETURNED_FOR_CORRECTIONS or
        old_status == ThesisStatus.IN_PROGRESS and new_status == ThesisStatus.DEFENDED
    )


def can_set_advisor(user: BaseUser, advisor: Optional[Employee]) -> bool:
    """Is the specified user permitted to set the given advisor (may be None)?"""
    return is_thesis_staff(user) or user == advisor


def can_cast_vote_as_user(caster: Employee, user: Employee) -> bool:
    """Can the specified user cast a vote in the other user's name?"""
    return is_admin(caster) or is_theses_board_member(user) and caster == user


def can_change_vote_for_thesis(user: Employee, thesis: Thesis) -> bool:
    """Can the specified user change votes for the specified thesis?"""
    return (
        is_admin(user) or
        is_theses_board_member(user) and ThesisStatus(thesis.status) not in UNVOTEABLE_STATUSES
    )


def can_see_thesis_rejection_reason(thesis: Thesis, is_staff: bool, user: BaseUser):
    """Should the official rejection reason be disclosed to the specified user?
    As an optimization, is_staff is passed directly so that we don't need to check
    that in this function (this will be called for every serialized thesis)
    """
    return is_staff or thesis.advisor == user or thesis.auxiliary_advisor == user


def can_see_thesis_votes(is_staff: bool):
    """Should the votes for a thesis be disclosed to this user?
    As above, this takes a bool argument as an optimization
    """
    return is_staff
