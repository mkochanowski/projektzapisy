from django.contrib.auth.models import User, Group as UserGroup
from apps.users.models import Employee, Student, PersonalDataConsent
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.course import CourseEntity, Course
from apps.enrollment.courses.models.course_type import Type
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.term import Term
from apps.enrollment.courses.models.classroom import Classroom
from apps.offer.vote.models import SystemState

import os
from time import sleep
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from django.db import connection
from django.core import mail

from django.conf import settings
from scripts.scheduleimport import run_test as scheduleimport_run_test
from scripts.ectsimport import run_test as ectsimport_run_test

sql_calls = [
            """
                CREATE TABLE courses_studentpointsview (
                    value smallint,
                    student_id integer,
                    entity_id integer
                );
            """
        ]

students, _ = UserGroup.objects.get_or_create(name='students')
employees, _ = UserGroup.objects.get_or_create(name='employees')

for sql_call in sql_calls:
        cursor = connection.cursor()
        cursor.execute(sql_call)
        connection.commit()

password = '11111'
admin = User.objects.create_superuser(username='przemka',
                                      password=password,
                                      email='admin@admin.com')

admin.first_name = 'przemka'
self.admin.save()
employees.user_set.add(admin)
employee = Employee.objects.create(user=admin)

employee_list = []
for i in range(1, 5):
    user = User.objects.create_user(
        username=('employee{}'.format(i)),
        password=self.password)
    user.first_name = 'Employee'
    user.last_name = str(i)
    user.save()
    employees.user_set.add(user)
    employee = Employee.objects.create(user=user)
    employee_list.append(employee)
employees.save()

student_list = []
for i in range(180):
    user = User.objects.create_user(
            username='student{}'.format(i),
            password=password)
    students.user_set.add(user)
    student = Student.objects.create(user=user)
    PersonalDataConsent.objects.update_or_create(student=student,
                                                 defaults={'granted': True})
    student_list.append(student)
students.save()
course_type = Type.objects.create(name='Informatyczny')
        # for i in range(1, 6):
        #     CourseEntity.objects.create(
        #         name='Course {}'.format(i),
        #         name_pl='Course {}'.format(i),
        #         name_en='Course {}'.format(i),
        #         semester='z',
        #         type=self.course_type,
        #         status=1,  # w ofercie
        #         suggested_for_first_year=False,
        #     )
        # for i in range(6, 11):
        #     CourseEntity.objects.create(
        #         name='Course {}'.format(i),
        #         name_pl='Course {}'.format(i),
        #         name_en='Course {}'.format(i),
        #         semester='l',
        #         type=self.course_type,
        #         status=1,  # w ofercie
        #         suggested_for_first_year=False,
        #     )
        # CourseEntity.objects.create(
        #     name='Course 50',
        #     semester='l',
        #     type=self.course_type,
        #     status=0,  # propozycja
        #     suggested_for_first_year=False,
        # )
        #
        # CourseEntity.objects.create(
        #     name='Course 100',
        #     semester='z',
        #     type=self.course_type,
        #     status=1,  # w ofercie
        #     suggested_for_first_year=False,
        # )
        #
        # CourseEntity.objects.create(
        #     name='Course 101',
        #     semester='l',
        #     type=self.course_type,
        #     status=1,  # w ofercie
        #     suggested_for_first_year=False,
        # )
        #
        # for course_entity in CourseEntity.objects.all():
        #     course_entity.owner = self.employee
        #     course_entity.save()
        #
        # self.winter_courses = ['Course 1', 'Course 2', 'Course 3']
        #
        # self.current_semester = Semester.objects.create(
        #     type=Semester.TYPE_SUMMER,
        #     year='1',
        #     semester_beginning=date.today(),
        #     semester_ending=date.today() + relativedelta(months=3),
        #     records_ects_limit_abolition=date.today() + relativedelta(days=10),
        #     visible=True,
        #     is_grade_active=False
        # )
        #
        # self.next_winter_semester = Semester.objects.create(
        #     type=Semester.TYPE_WINTER,
        #     year='2',
        #     semester_beginning=self.current_semester.semester_ending +
        #     relativedelta(
        #         days=1),
        #     semester_ending=self.current_semester.semester_ending +
        #     relativedelta(
        #         days=1,
        #         months=3),
        #     records_ects_limit_abolition=self.current_semester.semester_ending +
        #     relativedelta(
        #         days=11),
        #     visible=True,
        #     is_grade_active=False)
        #
        # self.next_summer_semester = Semester.objects.create(
        #     type=Semester.TYPE_SUMMER,
        #     year='3',
        #     semester_beginning=self.next_winter_semester.semester_ending +
        #     relativedelta(
        #         days=1),
        #     semester_ending=self.next_winter_semester.semester_ending +
        #     relativedelta(
        #         days=1,
        #         months=3),
        #     records_ects_limit_abolition=self.next_winter_semester.semester_ending +
        #     relativedelta(
        #         days=11),
        #     visible=True,
        #     is_grade_active=False)
        #
        # self.system_state = SystemState.objects.create(
        #     semester_winter=self.next_winter_semester,
        #     semester_summer=self.next_summer_semester,
        #     max_points=12,
        #     max_vote=3
        # )