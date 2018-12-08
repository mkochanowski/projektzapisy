from django.contrib.auth.models import User

from .models import Thesis, ThesisStatus
from .user_type import ThesisUserType, get_user_type


def can_add_thesis(user_type: ThesisUserType) -> bool:
    return user_type != ThesisUserType.student


def is_thesis_staff(user_type: ThesisUserType) -> bool:
    return user_type in [ThesisUserType.admin, ThesisUserType.theses_board_member]


def can_modify_thesis(user: User, thesis: Thesis):
    user_type = get_user_type(user)
    if (is_thesis_staff(user_type)):
        return True
    return thesis.advisor.pk == user.pk


def can_set_status(user_type: ThesisUserType, status: ThesisStatus):
    return (
        is_thesis_staff(user_type) or
        status == ThesisStatus.being_evaluated
    )


def can_set_advisor(user: User, user_type: ThesisUserType, advisor: User):
    user_type = get_user_type(user)
    if (is_thesis_staff(user_type)):
        return True
    return user.pk == advisor.pk
