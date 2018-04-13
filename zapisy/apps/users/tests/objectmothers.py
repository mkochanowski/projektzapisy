# -*- coding: utf-8 -*-

from apps.users.models import User, Employee


class UserObjectMother():

    @staticmethod
    def user_jan_kowalski():
        user = User(first_name="Jan",
                    last_name="Kowalski",
                    is_staff=False,
                    is_superuser=False,
                    username="jkowalski",
                    password="jkowalski")
        user.full_clean()
        return user

    @staticmethod
    def employee(user):
        employee = Employee(user=user)
        employee.full_clean()
        return employee
