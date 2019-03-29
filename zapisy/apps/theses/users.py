"""Defines various utility functions related to operations
on users of the theses system"""
from enum import Enum

from django.contrib.auth.models import User
from apps.users.models import BaseUser, Employee, Student, is_user_in_group

THESIS_BOARD_GROUP_NAME = "Komisja prac dyplomowych"


def is_student(user: BaseUser) -> bool:
    """Determine if the specified user is a student"""
    return get_user_type(user) == ThesisUserType.STUDENT


def is_theses_board_member(user: BaseUser) -> bool:
    """Is the specified user a member of the theses board?"""
    return is_user_in_group(user.user, THESIS_BOARD_GROUP_NAME)


def is_admin(user: BaseUser):
    return get_user_type(user) == ThesisUserType.ADMIN


def is_regular_employee(user: BaseUser):
    return get_user_type(user) == ThesisUserType.REGULAR_EMPLOYEE


def get_theses_board():
    """Return all members of the theses board"""
    return Employee.objects.select_related(
        "user"
    ).filter(user__groups__name=THESIS_BOARD_GROUP_NAME)


def get_num_board_members() -> int:
    """Return the number of theses board members"""
    return len(get_theses_board())


class ThesisUserType(Enum):
    STUDENT = 0
    REGULAR_EMPLOYEE = 1
    ADMIN = 2
    NONE = 3


def get_user_type(base_user: BaseUser) -> ThesisUserType:
    """Given a user, return their role in the thesis system
    The roles are based on group membership"""
    if isinstance(base_user, Employee):
        if base_user.user.is_staff:
            return ThesisUserType.ADMIN
        return ThesisUserType.REGULAR_EMPLOYEE
    elif isinstance(base_user, Student):
        return ThesisUserType.STUDENT
    return ThesisUserType.NONE


def get_theses_user_full_name(user: BaseUser):
    """Returns the full name of the user for use by the theses system.
    If the user is an Employee, `get_full_name_with_academic_title` will be used;
    otherwise, `get_full_name` will be used.
    """
    if isinstance(user, Employee):
        return user.get_full_name_with_academic_title()
    return user.get_full_name()
