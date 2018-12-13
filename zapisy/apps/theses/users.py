from enum import Enum

from django.contrib.auth.models import Group
from apps.users.models import BaseUser, Employee, Student, is_user_in_group

THESIS_BOARD_MEMBER_GROUP_NAME = "Członek komisji prac dyplomowych"


def is_theses_board_member(user: BaseUser) -> bool:
    return is_user_in_group(user.user, THESIS_BOARD_MEMBER_GROUP_NAME)


def get_num_board_members() -> int:
    return Group.objects.filter(name=THESIS_BOARD_MEMBER_GROUP_NAME).count()


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
            if is_theses_board_member(base_user)
            else ThesisUserType.employee
        )
    elif isinstance(base_user, Student):
        return ThesisUserType.student
    return ThesisUserType.none
