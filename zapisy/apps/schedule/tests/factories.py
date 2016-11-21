# -*- coding: utf-8 -*-

from datetime import date

from django.contrib.auth.models import User

from factory.django import DjangoModelFactory
from factory import SubFactory

from apps.schedule.models import Event, Term
from apps.enrollment.courses.models.course import Course, CourseEntity
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import ChangedDay
import common

DATE_THURSDAY = date(2017, 1, 5)


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


class ChangedDayFactory(DjangoModelFactory):
    class Meta:
        model = ChangedDay

    day = DATE_THURSDAY
    weekday = common.FRIDAY


class EventClassFactory(DjangoModelFactory):
    class Meta:
        model = Event

    type = Event.TYPE_CLASS
    visible = True
    status = Event.STATUS_ACCEPTED
    author = SubFactory(UserFactory)


class TermForEventClassFactory(DjangoModelFactory):
    class Meta:
        model = Term

    event = SubFactory(EventClassFactory)
    day = DATE_THURSDAY
