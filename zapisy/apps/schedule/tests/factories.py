# -*- coding: utf-8 -*-

from datetime import time

import factory
from factory.django import DjangoModelFactory

from apps.users.tests.factories import UserFactory
from apps.enrollment.courses.tests.factories import GroupFactory, SummerSemesterFactory, \
    ClassroomFactory
from apps.schedule.models import Event, Term, SpecialReservation
import common


class EventCourseFactory(DjangoModelFactory):
    class Meta:
        model = Event

    group = factory.SubFactory(GroupFactory)
    author = factory.SubFactory(UserFactory)


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    type = Event.TYPE_GENERIC
    visible = True
    status = Event.STATUS_ACCEPTED
    author = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: 'wydarzenie%d' % n)
    description = title


class ExamEventFactory(EventFactory):
    class Meta:
        model = Event

    type = Event.TYPE_EXAM


class TermFactory(DjangoModelFactory):
    class Meta:
        model = Term

    event = factory.SubFactory(EventFactory)
    room = factory.SubFactory(ClassroomFactory)
    day = factory.Faker('date_time_this_year', after_now=True)
    start = time(10)
    end = time(12)


class SepcialReservationFactory(DjangoModelFactory):
    class Meta:
        model = SpecialReservation

    semester = factory.SubFactory(SummerSemesterFactory)
    title = factory.Sequence(lambda n: 'Special reservation %d' % n)
    classroom = factory.SubFactory(ClassroomFactory)
    dayOfWeek = common.FRIDAY
    start_time = time(10, 15)
    end_time = time(12)
