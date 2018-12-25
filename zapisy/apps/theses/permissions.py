from apps.users.models import Employee, BaseUser

from .models import Thesis, ThesisStatus
from .users import ThesisUserType, get_user_type


def is_thesis_staff(user_type: ThesisUserType) -> bool:
    """Is this user a theses staff member, that is the system admin or a board member?"""
    return user_type in [ThesisUserType.admin, ThesisUserType.theses_board_member]


def can_add_thesis(user: BaseUser) -> bool:
    """Is the given user permitted to add new thesis objects?"""
    user_type = get_user_type(user)
    return user_type != ThesisUserType.student


def is_owner_of_thesis(user: BaseUser, thesis: Thesis) -> bool:
    """Is the specified user the advisor of the specified thesis?"""
    return thesis.advisor and thesis.advisor.pk == user.pk


def can_modify_thesis(user: BaseUser, thesis: Thesis) -> bool:
    """Is the specified user permitted to make any changes to the specified thesis?"""
    user_type = get_user_type(user)
    return (
        is_thesis_staff(user_type) or
        is_owner_of_thesis(user, thesis)
    )


def can_change_title(user: BaseUser, thesis: Thesis) -> bool:
    """Is the specified user permitted to change the title of the specified thesis?"""
    user_type = get_user_type(user)
    return (
        is_thesis_staff(user_type) or
        is_owner_of_thesis(user, thesis) and thesis.status != ThesisStatus.accepted.value
    )


def can_set_status(user_type: ThesisUserType, status: ThesisStatus) -> bool:
    """Can a user of the specified type set the specified status for a new thesis?"""
    return (
        is_thesis_staff(user_type) or
        status == ThesisStatus.being_evaluated
    )


def can_modify_status(user_type: ThesisUserType) -> bool:
    """Can a user of the specified type modify an existing thesis' status?"""
    return is_thesis_staff(user_type)


def can_set_advisor(user: BaseUser, user_type: ThesisUserType, advisor: Employee) -> bool:
    """Is the specified user permitted to set the given advisor (may be None)?"""
    user_type = get_user_type(user)
    return is_thesis_staff(user_type) or advisor and user.pk == advisor.pk
