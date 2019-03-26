"""Defines various utility functions related to operations
on users of the theses system"""
from enum import Enum

from django.http import Http404
from django.contrib.auth.models import User
from apps.users.models import BaseUser, Employee, Student, is_user_in_group
from .system_settings import get_master_rejecter

THESIS_BOARD_GROUP_NAME = "Komisja prac dyplomowych"


def is_student(user: BaseUser) -> bool:
    """Determine if the specified user is a student"""
    return get_user_type(user) == ThesisUserType.STUDENT


def is_theses_board_member(user: BaseUser) -> bool:
    """Is the specified user a member of the theses board?"""
    return is_user_in_group(user.user, THESIS_BOARD_GROUP_NAME)


def is_master_rejecter(user: BaseUser) -> bool:
    """Is the specified user the master rejecter
    (the board member responsible for rejecting theses)?
    """
    return get_master_rejecter() == user


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


def get_theses_user_full_name(user: BaseUser):
    """Returns the full name of the user for use by the theses system.
    If the user is an Employee, `get_full_name_with_academic_title` will be used;
    otherwise, `get_full_name` will be used.
    """
    if isinstance(user, Employee):
        return user.get_full_name_with_academic_title()
    return user.get_full_name()
