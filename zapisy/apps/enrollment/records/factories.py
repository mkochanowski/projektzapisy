# -*- coding: utf-8 -*-

import factory
import factory.fuzzy
import re
from django.contrib.auth.models import User
from apps.users.models import UserProfile, Student, Employee
from apps.enrollment.courses.models import Group, Course, CourseEntity, \
    Semester
from random import randint
from datetime import datetime

# taken from branch theses, should be merged
# theses/zapisy/apps/theses/user_factories.py


def alphanum(string):
    return re.sub(r'\W+', '', string)


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory('apps.theses.user_factories.UserFactory',
                              profile=None)
    is_student = True
    is_employee = False
    is_zamawiany = False


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student
    user = factory.SubFactory('apps.theses.user_factories.StudentUserFactory',
                              student=None)


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee
    user = factory.SubFactory('apps.theses.user_factories.EmployeeUserFactory',
                              employee=None)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: 'user_{0}'.format(n))
    first_name = username
    last_name = username
    email = factory.LazyAttribute(
        lambda obj: alphanum(obj.first_name) + '.' +
        alphanum(obj.last_name) + '@ii.uni.wroc.pl')
    password = 'pass'
    is_staff = False

    profile = factory.RelatedFactory(UserProfileFactory, 'user')


class EmployeeUserFactory(UserFactory):
    class Meta:
        model = User

    profile = factory.RelatedFactory(UserProfileFactory, 'user',
                                     is_student=False, is_employee=True)
    employee = factory.RelatedFactory(EmployeeFactory, 'user')


class StudentUserFactory(UserFactory):
    class Meta:
        model = User

    profile = factory.RelatedFactory(UserProfileFactory, 'user')
    student = factory.RelatedFactory(StudentFactory, 'user')


# up to this point
class SemesterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Semester
        exclude = ('whole_year', )
    visible = True
    type = factory.Iterator([Semester.TYPE_WINTER, Semester.TYPE_SUMMER])
    whole_year = factory.fuzzy.FuzzyInteger(2010, 2020)
    year = \
        factory.LazyAttribute(lambda x: ("%s/%s" % (x.whole_year,
                                                    x.whole_year % 100 + 1)))
    if type == Semester.TYPE_WINTER:
        records_opening = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 9, 20))
        records_closing = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 10, 31))
        lectures_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 10, 1))
        lectures_ending = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 1, 31))
        semester_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 10, 1))
        semester_ending = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 2, 22))
        records_ects_limit_abolition =  \
            factory.LazyAttribute(lambda x: datetime(x.whole_year-1, 10, 1))
    else:
        records_opening = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 2, 1))
        records_closing = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 3, 15))
        lectures_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 2, 25))
        lectures_ending = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 6, 15))
        semester_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 2, 25))
        semester_ending = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 9, 30))
        records_ects_limit_abolition = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 3, 1))


class CourseEntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseEntity
    name = factory.Sequence(lambda n: 'course_entity_{0}'.format(n))


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course
    lectures = 30
    exercises = 30
    laboratories = 30
    entity = factory.RelatedFactory(CourseEntityFactory)
    semester = factory.RelatedFactory(SemesterFactory)
    type = 1
    name = factory.Sequence(lambda n: 'course_{0}'.format(n))
