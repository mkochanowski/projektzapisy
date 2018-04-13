# -*- coding: utf-8 -*-

import factory.fuzzy
from factory.django import DjangoModelFactory

from apps.users.models import User, Student, Employee
from django.conf import settings

langs = [x[0] for x in settings.LANGUAGES]


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        # factory is pretty stupid, and will not remember if
        # user was created for other factory
        exclude = ("pref_username", "suff_username", )

    pref_username = factory.Sequence(lambda n: 'testuser_{0}'.format(n))
    suff_username = ""
    username = factory.LazyAttribute(lambda o: o.pref_username + o.suff_username)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    is_staff = False
    is_superuser = False
    email = factory.LazyAttribute(lambda o: o.pref_username + o.suff_username + '@example.com')


class StudentFactory(DjangoModelFactory):
    class Meta:
        model = Student

    user = factory.SubFactory(UserFactory, suff_username="_s")
    matricula = factory.Sequence(lambda n: ('9%05d' % n))

class EmployeeFactory(DjangoModelFactory):
    class Meta:
        model = Employee

    user = factory.SubFactory(UserFactory, suff_username="_e")
