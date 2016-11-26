# -*- coding: utf-8 -*-

from datetime import time, datetime, date

from apps.users.models import User, Student

import factory
from factory.django import DjangoModelFactory

from apps.schedule.models import Event, Term, SpecialReservation
from apps.enrollment.courses.models.course import Course, CourseEntity
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import ChangedDay, Semester
from apps.enrollment.courses.models.classroom import Classroom
import common


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user%d' % n)


class StudentFactory(DjangoModelFactory):
    class Meta:
        model = Student

    user = factory.SubFactory(UserFactory)


class CourseEntityFactory(DjangoModelFactory):
    class Meta:
        model = CourseEntity


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    entity = factory.SubFactory(CourseEntityFactory)


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    course = factory.SubFactory(CourseFactory)


class EventCourseFactory(DjangoModelFactory):
    class Meta:
        model = Event

    group = factory.SubFactory(GroupFactory)
    author = factory.SubFactory(UserFactory)


class ChangedDayForFridayFactory(DjangoModelFactory):
    class Meta:
        model = ChangedDay

    weekday = common.FRIDAY


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    type = Event.TYPE_GENERIC
    visible = True
    status = Event.STATUS_ACCEPTED
    author = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: 'wydarzenie%d' % n)


class ClassroomFactory(DjangoModelFactory):
    class Meta:
        model = Classroom

    number = '25'
    can_reserve = True
    type = 0
    floor = 0


class TermFactory(DjangoModelFactory):
    class Meta:
        model = Term

    event = factory.SubFactory(EventFactory)
    room = factory.SubFactory(ClassroomFactory)


class SummerSemesterFactory(DjangoModelFactory):
    class Meta:
        model = Semester

    visible = True
    type = Semester.TYPE_WINTER
    semester_beginning = date(datetime.now().year + 1, 2, 15)
    semester_ending = date(datetime.now().year + 1, 6, 30)
    lectures_beginning = semester_beginning
    lectures_ending = semester_ending


class SepcialReservationFactory(DjangoModelFactory):
    class Meta:
        model = SpecialReservation

    semester = factory.SubFactory(SummerSemesterFactory)
    title = factory.Sequence(lambda n: 'Special reservation %d' % n)
    classroom = factory.SubFactory(ClassroomFactory)
    dayOfWeek = common.FRIDAY
    start_time = time(10, 15)
    end_time = time(12)
