# -*- coding: utf-8 -*-

from django.test import TestCase

from django.contrib.auth.models import User
from apps.enrollment.courses.models import Group, Course, CourseEntity, Semester
from apps.enrollment.records.utils import run_rearanged
from apps.users.models import Student, Employee
from django.db import connection

from datetime import datetime

class DummyTest(TestCase):
    def createSemester(self):
        semester = Semester(
            visible=True,
            type=Semester.TYPE_WINTER,
            year='2016/17',
            records_opening=datetime(2016, 9, 20),
            records_closing=datetime(2016, 11, 14),
            lectures_beginning=datetime(2016, 11, 10),
            lectures_ending=datetime(2017, 2, 3),
            semester_beginning=datetime(2016, 11, 10),
            semester_ending=datetime(2017, 2, 21),
            records_ects_limit_abolition=datetime(2015, 10, 1))
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
            limit=10,
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

    def initialize_triggers(self):
        sql_minutes_view = """
            CREATE VIEW users_minutes_bonus_view AS
            SELECT us.id AS student_id,
                cs.id AS semester_id,
                ((((((( SELECT count(*) AS count
                    FROM ticket_create_studentgraded
                    WHERE ((ticket_create_studentgraded.semester_id = ANY (ARRAY[cs.first_grade_semester_id, cs.second_grade_semester_id])) AND (ticket_create_studentgraded.student_id = us.id))) * 1440) + (us.ects * 5)) + (((us.ects * 5) / 720) * 720)) + us.records_opening_bonus_minutes) + 120))::integer AS minutes
            FROM users_student us,
                courses_semester cs
            WHERE (cs.records_closing > now());
        """
        sql_view = """
            CREATE VIEW users_openingtimesview_unmaterialized AS
            SELECT cc.id AS course_id,
                users_student.id AS student_id,
                cc.semester_id,
                GREATEST(cc.records_start, (cs.records_opening - ((((v.minutes + (COALESCE(( SELECT DISTINCT sv.correction
                    FROM vote_singlevote sv
                    WHERE ((sv.student_id = users_student.id) AND (sv.correction > 0) AND (sv.entity_id = cc.entity_id) AND (sv.state_id IN ( SELECT vs.id
                            FROM vote_systemstate vs
                            WHERE ((vs.semester_summer_id = cc.semester_id) OR (vs.semester_winter_id = cc.semester_id)))))
                    LIMIT 1), 0) * 1440)))::text || ' MINUTES'::text))::interval)) AS opening_time
            FROM courses_course cc,
                users_student,
                (courses_semester cs
                LEFT JOIN users_minutes_bonus_view v ON ((v.semester_id = cs.id)))
            WHERE ((users_student.status = 0) AND ((v.student_id IS NULL) OR (v.student_id = users_student.id)) AND (cs.records_opening IS NOT NULL) AND (cc.semester_id = cs.id) AND ((cs.records_closing > now()) OR ((cc.records_start IS NOT NULL) AND (cc.records_end IS NOT NULL) AND (cc.records_end > now()))));
        """
        sql_function = """
            CREATE FUNCTION users_openingtimesview_refresh_for_semester(id integer) RETURNS void
            LANGUAGE plpgsql SECURITY DEFINER
            AS $$
                begin
                delete from users_openingtimesview csp where csp.semester_id = id;
                insert into users_openingtimesview
                SELECT * FROM users_openingtimesview_unmaterialized scp
                    WHERE scp.semester_id = id;
                end
                $$;
        """

        sql_calls = [
                """
                CREATE TABLE courses_studentpointsview (
                    value smallint,
                    student_id integer,
                    entity_id integer
                );
                """
                ]
        cursor = connection.cursor()
        cursor.execute(sql_minutes_view)
        connection.commit()

        cursor = connection.cursor()
        cursor.execute(sql_view)
        connection.commit()

        cursor = connection.cursor()
        cursor.execute(sql_function)
        connection.commit()

        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()

    def refresh_opening_times(self, semester):
        cursor = connection.cursor()
        cursor.execute("SELECT users_openingtimesview_refresh_for_semester(%s);" % str(semester.id))
        connection.commit()

    def testDummy(self):
        self.assertTrue(True)

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
