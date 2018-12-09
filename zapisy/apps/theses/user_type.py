from enum import Enum

from apps.users.models import BaseUser, Employee, Student
from . import models


class ThesisUserType(Enum):
    student = 0
    employee = 1
    theses_board_member = 2
    admin = 3
    none = 4


def get_user_type(base_user: BaseUser) -> ThesisUserType:
    if isinstance(base_user, Employee):
        if base_user.user.is_staff:
            return ThesisUserType.admin
        return (
            ThesisUserType.theses_board_member
            if models.is_theses_board_member(base_user)
            else ThesisUserType.employee
        )
    elif isinstance(base_user, Student):
        return ThesisUserType.student
    return ThesisUserType.none
