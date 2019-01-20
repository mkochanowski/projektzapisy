from django.contrib.auth.models import User, Group as UserGroup
from apps.users.models import Employee, Student, PersonalDataConsent
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.course import CourseEntity, Course
from apps.enrollment.courses.models.course_type import Type
from apps.enrollment.courses.models.group import Group
from apps.offer.vote.models import SystemState

from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from django.db import connection


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
admin.save()
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

COMPULSORY_COURSES = {
    "Logika": 8,
    "AnalMat": 10,
    "LogikaZ": 8,
}

VOLUNTARY_COURSES = {
    "PWI": 3,
    "WdC": 5,
    "WdPython": 5,
    "WDI": 6,
    "MD": 6
}

course_type = Type.objects.create(name='Informatyczny')
for name, ects in COMPULSORY_COURSES:
    CourseEntity.objects.create(
        name=name,
        name_pl=name,
        name_en=name,
        semester='z',
        type=course_type,
        status=1,  # w ofercie
        suggested_for_first_year=True,
        ects=ects
    )

for name, ects in VOLUNTARY_COURSES:
    CourseEntity.objects.create(
        name=name,
        name_pl=name,
        name_en=name,
        semester='z',
        type=course_type,
        status=1,  # w ofercie
        suggested_for_first_year=True,
        ects=ects
    )

for course_entity in CourseEntity.objects.all():
    course_entity.owner = employee
    course = Course.objects.create(entity=course_entity)
    for i in range(4):
        Group.objects.create(
            course=course,
            teacher=employee,
            limit=30,
            type='ćwiczenia'
        )
    course_entity.save()

winter_courses = ['Course 1', 'Course 2', 'Course 3']
current_semester = Semester.objects.create(
    type=Semester.TYPE_WINTER,
    year='1',
    semester_beginning=date.today(),
    semester_ending=date.today() + relativedelta(months=3),
    records_ects_limit_abolition=date.today() + relativedelta(days=10),
    visible=True,
    is_grade_active=False
)

next_summer_semester = Semester.objects.create(
    type=Semester.TYPE_SUMMER,
    year='2',
    semester_beginning=current_semester.semester_ending + relativedelta(days=1),
    semester_ending=current_semester.semester_ending + relativedelta(days=1, months=3),
    records_ects_limit_abolition=current_semester.semester_ending + relativedelta(days=11),
    visible=True,
    is_grade_active=False)

next_winter_semester = Semester.objects.create(
    type=Semester.TYPE_WINTER,
    year='3',
    semester_beginning=next_summer_semester.semester_ending + relativedelta(days=1),
    semester_ending=next_summer_semester.semester_ending + relativedelta(days=1, months=3),
    records_ects_limit_abolition=next_summer_semester.semester_ending + relativedelta(days=11),
    visible=True,
    is_grade_active=False)

system_state = SystemState.objects.create(
    semester_winter=next_winter_semester,
    semester_summer=next_summer_semester,
    max_points=12,
    max_vote=3
)
