# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from factory.django import DjangoModelFactory
from factory import SubFactory

from apps.schedule.models import Event
from apps.enrollment.courses.models.course import Course, CourseEntity
from apps.enrollment.courses.models.group import Group


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class CourseEntityFactory(DjangoModelFactory):
    class Meta:
        model = CourseEntity


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    entity = SubFactory(CourseEntityFactory)


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    course = SubFactory(CourseFactory)


class EventCourseFactory(DjangoModelFactory):
    class Meta:
        model = Event

    group = SubFactory(GroupFactory)
    author = SubFactory(UserFactory)
