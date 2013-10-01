# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse
from apps.enrollment.records.models import Queue, Record
from apps.users.models import Student
from apps.enrollment.courses.models import Semester, Group, CourseEntity, Course


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


@permission_required('courses.view_stats')
def swap(request):
    semester = Semester.objects.get_next()
    courses = Course.objects.filter(semester=semester)

    types = [ ('2', 'ćwiczenia'), ('3', 'pracownia'),
        ('5', 'ćwiczenio-pracownia'),
        ('6', 'seminarium'), ('10', 'projekt')]

    for course in Course.objects.filter(semester=semester):
        course.groups_items = []

        for type in types:
            groups = Group.objects.filter(course=course, type=type[0])
            students = {}
            lists = {}
            used = []

            for g in groups:
                lists[g.id] = []
                for r in Record.objects.filter(group=g, status=1).select_related('student', 'student__user'):
                    lists[g.id].append(r)
                    students[r.student_id] = g

            for group in groups:
                group.swaps = []
                queue = Queue.objects.filter(group=group, deleted=False).select_related('student', 'student__user')
                for s in queue:
                    for sp in lists[group.id]:
                        if students[sp.student_id] == group and sp.student_id not in used:
                            used.append(sp.student_id)
                            group.swaps.append({
                                'student_in_queue': sp.student,
                                'student_in_group': s.student,
                                'to': students[sp.student_id]
                            })

                course.groups_items.append(group)

    return TemplateResponse(request, 'statistics/swap.html', locals())
