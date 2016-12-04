# -*- coding: utf-8 -*-

import factory
from factory.django import DjangoModelFactory

from ..models import User, Student


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user%d' % n)
    password = username
    is_staff = False
    is_superuser = False


class StudentFactory(DjangoModelFactory):
    class Meta:
        model = Student

    user = factory.SubFactory(UserFactory)
    matricula = factory.Sequence(lambda n: ('%06d' % n))
