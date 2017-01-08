# -*- coding: utf-8 -*-

from django.test import TestCase

from django.contrib.auth.models import User
from apps.enrollment.courses.models import Group, Course, CourseEntity, \
    Semester, StudentPointsView
from apps.enrollment.records.utils import run_rearanged
from apps.users.models import Student, Employee
from django.db import connection
from apps.enrollment.courses.tests.factories import GroupFactory
from apps.users.tests.factories import StudentFactory
from apps.users.models import OpeningTimesView
from apps.enrollment.records.models import Record, Queue, \
    STATUS_ENROLLED, STATUS_REMOVED


from datetime import datetime, timedelta
import time
from random import seed, randint, choice


class DummyTest(TestCase):
    reset_sequences = True


    def createSemester(self):
        today = datetime.now()
        semester = Semester(
            visible=True,
            type=Semester.TYPE_WINTER,
            year='2016/17',
            records_opening=(today + timedelta(days=-1)),
            records_closing=today + timedelta(days=6),
            lectures_beginning=today + timedelta(days=4),
            lectures_ending=today + timedelta(days=120),
            semester_beginning=today,
            semester_ending=today + timedelta(days=130),
            records_ects_limit_abolition=(today + timedelta(days=1)))
        semester.save()
        return semester

    def createStudentUser(self):
        user = User(
            username='jdz',
            first_name='Jan',
            last_name='Dzban',
            is_active=True)
        user.save()
        student = Student(
            matricula='221135',
            user=user)
        student.save()
        return user

    def createTeacher(self):
        user = User(
            username='klo',
            is_active=True)
        user.save()
        employee = Employee(user=user)
        employee.save()
        return (user, employee)

    def createCourse(self, semester):
        entity = CourseEntity(name = "Algorytmy i Struktury Danych")
        entity.save()
        course = Course(
            lectures = 30,
            exercises = 30,
            laboratories = 30,
            entity = entity,
            semester = semester,
            type = 1,
            name = "Algorytmy i Struktury Danych")
        course.save()
        return course

    def createExerciseGroup(self, course, teacher):
        group = Group(
            type=2,
            limit=5,
            course = course,
            teacher = teacher)
        group.save()
        return group

    def createLectureGroup(self, course, teacher):
        group = Group(
            type=1,
            limit=100,
            course = course,
            teacher = teacher)
        group.save()
        return group

    def setUp(self):
        sql_calls = [
            """
                CREATE TABLE courses_studentpointsview (
                    value smallint,
                    student_id integer,
                    entity_id integer
                );
            """
            ]

        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()

    def tearDown(self):
        sql_calls = [
            "DROP TABLE courses_studentpointsview;",
        ]
        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()


    def refresh_opening_times(self, semester):
        cursor = connection.cursor()
        cursor.execute("SELECT users_openingtimesview_refresh_for_semester(%s);" % str(semester.id))
        connection.commit()

        """
    def testAddStudentToLectureGroupOnly(self):
        self.initialize_triggers()
        student = self.createStudentUser()
        teacherUser, teacher = self.createTeacher()

        semester = self.createSemester()
        course = self.createCourse(semester)
        exercise_group = self.createExerciseGroup(course, teacher)
        lecture_group = self.createLectureGroup(course, teacher)

        self.refresh_opening_times(semester)

        result, messages_list = lecture_group.enroll_student(student.student)
        run_rearanged(result)
        self.assertTrue(result)
        self.assertEqual(messages_list, [u'Student dopisany do grupy'])
        """

    def testAddStudentToGroup(self):
        today = datetime.now()
        group = GroupFactory(
            course__semester__records_opening=today+timedelta(days=-1),
            course__semester__records_closing=today+timedelta(days=6)
        )
        student = StudentFactory()
        OpeningTimesView.objects.create(
            student=student, course=group.course,
            semester=group.course.semester, opening_time=today)
        result, messages_list = group.enroll_student(student)
        run_rearanged(result)
        self.assertTrue(result)
        self.assertEqual(messages_list, [u'Student dopisany do grupy'])

    def testAddStudentToQueue(self):
        today = datetime.now()
        group = GroupFactory(
            course__semester__records_opening=today+timedelta(days=-1),
            course__semester__records_closing=today+timedelta(days=6),
        )
        students = StudentFactory.create_batch(15)
        for student in students:
            OpeningTimesView.objects.create(
                student=student, course=group.course,
                semester=group.course.semester, opening_time=today)
        for student in students[:10]:
            result, messages_list = group.enroll_student(student)
            run_rearanged(result)
            self.assertTrue(result)
            self.assertEqual(messages_list, [u'Student dopisany do grupy'])
            # what the hell
            group.enrolled += 1
        for student in students[10:]:
            result, messages_list = group.enroll_student(student)
            run_rearanged(result)
            self.assertTrue(result)
            self.assertEqual(messages_list, [
                u'Brak wolnych miejsc w grupie',
                u'Student został dopisany do kolejki'])
        self.assertEqual(group.enrolled, 10)
        self.assertEqual(group.queued, 5)
