# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse
from apps.users.models import Student
from apps.enrollment.courses.models import Semester, Group, CourseEntity


@permission_required('courses.view_stats')
def main(request):
    return TemplateResponse(request, 'statistics/base.html')

#@permission_required('courses.view_stats')
#def students(request):
#    students = Student.objects.get_list_full_info().order_by('t0_min')
#    return TemplateResponse(request, 'statistics/students_list.html', locals())


@permission_required('courses.view_stats')
def students(request):
    students = Student.objects.get_list_full_info().\
        extra(select={'semester_points': "SELECT SUM(value) FROM (SELECT \
   courses_studentpointsview.value as value \
FROM courses_course LEFT JOIN courses_group ON (courses_group.course_id = courses_course.id) \
INNER JOIN records_record ON(records_record.group_id = courses_group.id) \
LEFT JOIN courses_studentpointsview ON (courses_studentpointsview.entity_id = courses_course.entity_id) \
WHERE courses_course.semester_id=329 AND courses_studentpointsview.student_id = users_student.id AND records_record.student_id = courses_studentpointsview.student_id AND records_record.status = '1' \
GROUP BY courses_course.id, courses_studentpointsview.value) as foo"}).\
        order_by('t0_min')
    return TemplateResponse(request, 'statistics/students_list.html', locals())


@permission_required('courses.view_stats')
def groups(request):
    semester = Semester.objects.get_next()
    groups = Group.statistics.in_semester(semester)
    return TemplateResponse(request, 'statistics/groups_list.html', locals())

@permission_required('courses.view_stats')
def votes(request):
    proposals = CourseEntity.statistics.in_year()
    return TemplateResponse(request, 'statistics/votes.html', locals())
