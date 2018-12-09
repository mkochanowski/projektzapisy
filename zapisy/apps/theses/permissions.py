from apps.users.models import Employee, BaseUser

from .models import Thesis, ThesisStatus
from .user_type import ThesisUserType, get_user_type


def is_thesis_staff(user_type: ThesisUserType) -> bool:
    return user_type in [ThesisUserType.admin, ThesisUserType.theses_board_member]


def can_add_thesis(user: BaseUser) -> bool:
    user_type = get_user_type(user)
    return user_type != ThesisUserType.student


def can_modify_thesis(user: BaseUser, thesis: Thesis):
    user_type = get_user_type(user)
    return is_thesis_staff(user_type) or thesis.advisor.pk == user.pk


def can_set_status(user_type: ThesisUserType, status: ThesisStatus):
    """
    Can a user of the specified type set the specified status for a new thesis?
    """
    return (
        is_thesis_staff(user_type) or
        status == ThesisStatus.being_evaluated
    )


def can_modify_status(user_type: ThesisUserType):
    """
    Can a user of the specified type modify an existing thesis' status?
    """
    return is_thesis_staff(user_type)


def can_set_advisor(user: BaseUser, user_type: ThesisUserType, advisor: Employee):
    """
    Is the specified user permitted to set the given advisor (may be None)?
    """
    user_type = get_user_type(user)
    return is_thesis_staff(user_type) or advisor and user.pk == advisor.pk
