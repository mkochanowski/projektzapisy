"""Defines various utility functions related to operations
on users of the theses system"""
from enum import Enum

from django.http import Http404
from django.contrib.auth.models import User
from apps.users.models import BaseUser, Employee, Student, is_user_in_group

THESIS_BOARD_GROUP_NAME = "Komisja prac dyplomowych"


def is_theses_board_member(user: BaseUser) -> bool:
    """Is the specified user a member of the theses board?"""
    return is_user_in_group(user.user, THESIS_BOARD_GROUP_NAME)


def is_admin(user: BaseUser):
    return get_user_type(user) == ThesisUserType.admin


def get_theses_board():
    """Return all members of the theses board"""
    return Employee.objects \
        .select_related("user") \
        .filter(user__groups__name=THESIS_BOARD_GROUP_NAME) \
        .all()


def get_num_board_members() -> int:
    """Return the number of theses board members"""
    return len(get_theses_board())


class ThesisUserType(Enum):
    student = 0
    employee = 1
    admin = 2
    none = 3


def get_user_type(base_user: BaseUser) -> ThesisUserType:
    """Given a user, return their role in the thesis system
    The roles are based on group membership"""
    if isinstance(base_user, Employee):
        if base_user.user.is_staff:
            return ThesisUserType.admin
        return ThesisUserType.employee
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
    raise Http404("invalid user")
