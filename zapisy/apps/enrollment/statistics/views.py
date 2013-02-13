# -*- coding: utf-8 -*-
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse
from apps.users.models import Student
from apps.enrollment.courses.models import Semester, Group

@permission_required('courses.view_stats')
def students_list(request):
    semester = Semester.objects.get_next()
    students = Student.objects.get_list_full_info().order_by('t0_min')
    groups   = Group.objects.filter(course__semester=semester).select_related('course').order_by('course')
    return TemplateResponse(request, 'statistics/students_list.html', locals())