from django.test import LiveServerTestCase

from django.contrib.auth.models import User, Group as UserGroup
from apps.users.models import Employee, Student, PersonalDataConsent
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.course import CourseEntity, Course
from apps.enrollment.courses.models.course_type import Type
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.term import Term
from apps.enrollment.courses.models.classroom import Classroom
from apps.offer.vote.models import SystemState

import os, re
from time import sleep
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from django.db import connection
from django.core import mail

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase

from scripts.scheduleimport import run_test as scheduleimport_run_test
from scripts.ectsimport import run_test as ectsimport_run_test


class NewSemestrTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
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
            # connection.commit()

        cls.password = '11111'
        cls.admin = User.objects.create_superuser(
            username='przemka', password=cls.password, email='admin@admin.com')

        cls.admin.first_name = 'przemka'
        cls.admin.save()
        employees.user_set.add(cls.admin)
        cls.employee = Employee.objects.create(user=cls.admin)

        cls.employees = []
        for i in range(1, 5):
            user = User.objects.create_user(
                username=('employee{}'.format(i)), password=cls.password)
            user.first_name = 'Employee'
            user.last_name = str(i)
            user.save()
            employees.user_set.add(user)
            employee = Employee.objects.create(user=user)
            cls.employees.append(employee)
        employees.save()

        user_student1 = User.objects.create_user(
            username='student1', password=cls.password)
        user_student2 = User.objects.create_user(
            username='student2', password=cls.password)
        user_student3 = User.objects.create_user(
            username='student3', password=cls.password)
        user_student4 = User.objects.create_user(
            username='student4', password=cls.password)

        students.user_set.add(user_student1)
        students.user_set.add(user_student2)
        students.user_set.add(user_student3)
        students.user_set.add(user_student4)
        students.save()

        cls.student1 = Student.objects.create(
            user=user_student1, matricula='264823')
        cls.student2 = Student.objects.create(
            user=user_student2, matricula='222222')
        cls.student3 = Student.objects.create(
            user=user_student3, matricula='333333')
        cls.student4 = Student.objects.create(
            user=user_student4, matricula='444444')
        PersonalDataConsent.objects.update_or_create(
            student=cls.student1, defaults={'granted': True})
        PersonalDataConsent.objects.update_or_create(
            student=cls.student2, defaults={'granted': True})
        PersonalDataConsent.objects.update_or_create(
            student=cls.student3, defaults={'granted': True})
        PersonalDataConsent.objects.update_or_create(
            student=cls.student4, defaults={'granted': True})
        cls.course_type = Type.objects.create(name='Informatyczny')
        for i in range(1, 6):
            CourseEntity.objects.create(
                name='Course {}'.format(i),
                name_pl='Course {}'.format(i),
                name_en='Course {}'.format(i),
                semester='z',
                type=cls.course_type,
                status=1,  # w ofercie
                suggested_for_first_year=False,
            )
        for i in range(6, 11):
            CourseEntity.objects.create(
                name='Course {}'.format(i),
                name_pl='Course {}'.format(i),
                name_en='Course {}'.format(i),
                semester='l',
                type=cls.course_type,
                status=1,  # w ofercie
                suggested_for_first_year=False,
            )
        CourseEntity.objects.create(
            name='Course 50',
            semester='l',
            type=cls.course_type,
            status=0,  # propozycja
            suggested_for_first_year=False,
        )

        CourseEntity.objects.create(
            name='Course 100',
            semester='z',
            type=cls.course_type,
            status=1,  # w ofercie
            suggested_for_first_year=False,
        )

        CourseEntity.objects.create(
            name='Course 101',
            semester='l',
            type=cls.course_type,
            status=1,  # w ofercie
            suggested_for_first_year=False,
        )

        for course_entity in CourseEntity.objects.all():
            course_entity.owner = cls.employee
            course_entity.save()

        cls.winter_courses = ['Course 1', 'Course 2', 'Course 3']

        cls.current_semester = Semester.objects.create(
            type=Semester.TYPE_SUMMER,
            year='1',
            semester_beginning=date.today(),
            semester_ending=date.today() + relativedelta(months=3),
            records_ects_limit_abolition=date.today() + relativedelta(days=10),
            visible=True,
            is_grade_active=False)

        cls.next_winter_semester = Semester.objects.create(
            type=Semester.TYPE_WINTER,
            year='2',
            semester_beginning=cls.current_semester.semester_ending +
            relativedelta(days=1),
            semester_ending=cls.current_semester.semester_ending +
            relativedelta(days=1, months=3),
            records_ects_limit_abolition=cls.current_semester.semester_ending +
            relativedelta(days=11),
            visible=True,
            is_grade_active=False)

        cls.next_summer_semester = Semester.objects.create(
            type=Semester.TYPE_SUMMER,
            year='3',
            semester_beginning=cls.next_winter_semester.semester_ending +
            relativedelta(days=1),
            semester_ending=cls.next_winter_semester.semester_ending +
            relativedelta(days=1, months=3),
            records_ects_limit_abolition=cls.next_winter_semester.
            semester_ending + relativedelta(days=11),
            visible=True,
            is_grade_active=False)

        cls.system_state = SystemState.objects.create(
            semester_winter=cls.next_winter_semester,
            semester_summer=cls.next_summer_semester,
            max_points=12,
            max_vote=3)

        cls.client = Client()

    @classmethod
    def tearDownTestData(cls) -> None:
        sql_calls = [
            'DROP TABLE courses_studentpointsview;',
        ]
        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()

    def test_new_semester_scenario(cls):
        cls.prepare_course_entities_for_voting()
        # cls.perform_voting()
        # cls.create_offer_for_winter_semester()
        # cls.perform_winter_correction()
        # cls.import_winter_schedule()
        # cls.start_winter_semester()
        # cls.add_new_students()
        # cls.import_ects()
        # cls.open_records()
        # cls.generate_t0()
        
    def prepare_course_entities_for_voting(cls):
        cls.client.post(
            "/fereol_admin/login/", {
                "username": cls.admin.username,
                "password": cls.password
            },
            follow=True)

        response = cls.client.get(
            "/offer/manage/select_for_voting", follow=True)

        all_options = len(
            re.findall('(<option.*?\/option>)', str(response.content)))
        selected_options = len(
            re.findall('(<option.*?selected="selected".*?\/option>)',
                       str(response.content)))
        nonselected_options = all_options - selected_options

        cls.assertEqual(
            CourseEntity.objects.filter(status=1).count(), nonselected_options)
        cls.assertEqual(
            CourseEntity.objects.filter(status=2).count(), selected_options)

        response = cls.client.post(
            "/offer/manage/select_for_voting", {
                'for_voting': [1,2,3,4,5,6,7,8,9,10]
            },
            follow=True)
