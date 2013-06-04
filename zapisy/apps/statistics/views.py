# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse
from apps.users.models import Student
from apps.enrollment.courses.models import Semester, Group, CourseEntity


@permission_required('courses.view_stats')
def main(request):
    return TemplateResponse(request, 'statistics/base.html')

@permission_required('courses.view_stats')
def students(request):
    students = Student.objects.get_list_full_info().order_by('t0_min')
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
