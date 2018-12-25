from django.contrib.auth.models import User

from apps.users.models import BaseUser


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
