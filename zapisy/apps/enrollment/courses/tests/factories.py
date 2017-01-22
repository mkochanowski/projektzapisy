# -*- coding: utf-8 -*-

from datetime import date, datetime

import factory
from factory.django import DjangoModelFactory

from ..models.course import Course, CourseEntity
from ..models.group import Group
from ..models.semester import ChangedDay, Semester
from ..models.classroom import Classroom
import common


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


class ChangedDayForFridayFactory(DjangoModelFactory):
    class Meta:
        model = ChangedDay

    weekday = common.FRIDAY


class SummerSemesterFactory(DjangoModelFactory):
    class Meta:
        model = Semester

    visible = True
    type = Semester.TYPE_SUMMER
    semester_beginning = date(datetime.now().year + 1, 2, 15)
    semester_ending = date(datetime.now().year + 1, 6, 30)
    lectures_beginning = semester_beginning
    lectures_ending = semester_ending
    records_ects_limit_abolition = datetime(datetime.now().year + 1, 2, 10)
    year = str(semester_beginning.year - 1) + "/" + str(semester_beginning.year % 100)
class WinterSemesterFactory(DjangoModelFactory):
    class Meta:
        model = Semester

    visible = True
    type = Semester.TYPE_WINTER
    semester_beginning = date(datetime.now().year + 1, 10, 01)
    semester_ending = date(datetime.now().year + 1, 12, 30)
    lectures_beginning = semester_beginning
    lectures_ending = semester_ending
    records_ects_limit_abolition = datetime(datetime.now().year + 1, 10, 10)
    year = str(semester_beginning.year - 1) + "/" + str(semester_beginning.year % 100)


class ClassroomFactory(DjangoModelFactory):
    class Meta:
        model = Classroom

    number = '25'
    can_reserve = True
    type = 0
    floor = 0
