from enum import Enum

from django.contrib.auth.models import Group, User
from apps.users.models import BaseUser, Employee, Student, is_user_in_group

THESIS_BOARD_GROUP_NAME = "Komisja prac dyplomowych"


def is_theses_board_member(user: BaseUser) -> bool:
    """Is the specified user a member of the theses board?"""
    return is_user_in_group(user.user, THESIS_BOARD_GROUP_NAME)


def get_num_board_members() -> int:
    """How many theses board members are there in total?"""
    return Group.objects.filter(name=THESIS_BOARD_GROUP_NAME).count()


class ThesisUserType(Enum):
    student = 0
    employee = 1
    theses_board_member = 2
    admin = 3
    none = 4


def get_user_type(base_user: BaseUser) -> ThesisUserType:
    """Given a user, return their role in the thesis system
    The roles are based on group membership"""
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


def wrap_user(user: User) -> BaseUser:
    """Given an instance of contrib.auth.models.User,
    wrap it into an instance of BaseUser.

    This is necessary because of legacy logic present in apps.users.models:
    all users are instances of Student or Employee (both subclasses of BaseUser),
    which link to their corresponding instance of Django's User with a OneToOneField.
    This is most likely legacy logic from the days when Django didn't offer the possibility
    to change the user auth model; if this is refactored,
    this function will not be necessary anymore.
    """

    if BaseUser.is_employee(user):
        return user.employee
    elif BaseUser.is_student(user):
        return user.student
    else:
        return user
