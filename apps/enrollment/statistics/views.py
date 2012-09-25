# -*- coding: utf-8 -*-
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from apps.users.models import Student
from apps.enrollment.courses.models import Semester, Group

@staff_member_required
def students_list(request):
    students = Student.get_list().order_by('t0')
    semester = Semester.get_current_semester()
    groups   = Group.get_all_in_semester(semester)
    return TemplateResponse(request, 'statistics/students_list.html', locals())