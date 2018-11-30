from enum import Enum

from django.contrib.auth.models import User

from apps.users.models import BaseUser
from . import models


class ThesisUserType(Enum):
    student = 0
    employee = 1
    theses_board_member = 2
    admin = 3


def get_user_type(user_instance: User) -> ThesisUserType:
    if user_instance.is_staff:
        return ThesisUserType.admin
    elif BaseUser.is_employee(user_instance):
        return (
            ThesisUserType.theses_board_member
            if models.is_theses_board_member(user_instance.employee)
            else ThesisUserType.employee
        )
    elif BaseUser.is_student(user_instance):
        return ThesisUserType.student
