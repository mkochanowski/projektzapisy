from django.contrib.auth.models import User

from apps.users.models import BaseUser


def wrap_user(user: User):
    if BaseUser.is_employee(user):
        return user.employee
    elif BaseUser.is_student(user):
        return user.student
    else:
        return user
