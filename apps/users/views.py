# -*- coding: utf-8 -*-

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.http import QueryDict, HttpResponse 
from django.utils import simplejson
from django.db.models import Q

from django.conf import settings

from apps.users.exceptions import NonUserException, NonEmployeeException,\
                                 NonStudentException
from apps.users.utils import prepare_ajax_students_list,\
                             prepare_ajax_employee_list

from apps.users.models import Employee, Student
from apps.enrollment.subjects.models import Semester, Group
from apps.enrollment.records.models import Record

from apps.users.forms import EmailChangeForm

from datetime import timedelta
from libs.ajax_messages import AjaxFailureMessage, AjaxSuccessMessage
import datetime

import logging
logger = logging.getLogger()

@login_required
def student_profile(request, user_id):
    """student profile"""
    try:
        student = Student.objects.get(user__pk=user_id)
        groups = Student.get_schedule(student)

        data = {
	            'groups' : groups,
	            'student' : student,
	        }

        if request.is_ajax():
            return render_to_response('users/ajax_student_profile.html', data, context_instance=RequestContext(request))
        else:
            begin = 'A'
            end   = 'B'
            char  = 'A'
            students = Student.get_list(begin, end)
            students = Record.recorded_students(students)
            data['students'] = students
            data['char']     = char
            return render_to_response('users/student_profile.html', data, context_instance=RequestContext(request))

    except NonStudentException:
        logger.error('Function student_profile(id = %d) throws NonStudentException while acessing to non existing student.' % int(user_id) )
        request.user.message_set.create(message="Nie ma takiego studenta.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
        logger.error('Function student_profile(id = %d) throws User.DoesNotExist while acessing to non existing user.' % int(user_id) )
        request.user.message_set.create(message="Nie ma takiego użytkownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@login_required
def employee_profile(request, user_id):
    """student profile"""
    try:
        user = User.objects.get(id=user_id)
        employee = user.employee
        groups = Employee.get_schedule(user.id)
        
        data = {
            'groups' : groups,
            'employee' : employee,
        }
        if request.is_ajax():
            return render_to_response('users/ajax_employee_profile.html', data, context_instance=RequestContext(request))
        else:
            begin = 'A'
            end   = 'B'
            char  = 'A'
            employees = Employee.get_list(begin, end)
            semester = Semester.get_current_semester()
            employees = Group.teacher_in_present(employees, semester)

            for e in employees:
                e.short_new = e.user.first_name[:1] + e.user.last_name[:2]
                e.short_old = e.user.first_name[:2] + e.user.last_name[:2]

            data['employees'] = employees
            data['char'] = char
              
            return render_to_response('users/employee_profile.html', data, context_instance=RequestContext(request))


    except NonEmployeeException:
        logger.error('Function employee_profile(user_id = %d) throws NonEmployeeException while acessing to non existing employee.' % user_id )
        request.user.message_set.create(message="Nie ma takiego pracownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
        logger.error('Function employee_profile(id = %d) throws User.DoesNotExist while acessing to non existing user.' % user_id )
        request.user.message_set.create(message="Nie ma takiego użytkownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    
@login_required
def email_change(request):
    '''function that enables mail changing'''
    if request.POST:
        data = request.POST.copy()
        form = EmailChangeForm(data, instance=request.user)
        if form.is_valid():
            form.save()
            logger.info('User (%s) changed email' % request.user.get_full_name())
            request.user.message_set.create(message="Twój adres e-mail został zmieniony.")
            return HttpResponseRedirect(reverse('my-profile'))
    else:
        form = EmailChangeForm({'email' : request.user.email})
    return render_to_response('users/email_change_form.html', {'form':form}, context_instance=RequestContext(request))

@login_required  
def password_change_done(request):
    '''informs if password were changed'''
    logger.info('User (%s) changed password' % request.user.get_full_name())
    request.user.message_set.create(message="Twóje hasło zostało zmienione.")
    return HttpResponseRedirect(reverse('my-profile'))
 
@login_required  
def my_profile(request):
    '''profile site'''
    logger.info('User %s <id: %s> is logged in ' % (request.user.username, request.user.id))
    current_semester = Semester.get_default_semester()
    zamawiany = Student.get_zamawiany(request.user.id)
    comments = zamawiany and zamawiany.comments or ''
    points = zamawiany and zamawiany.points or 0
    if current_semester:
        try:
            point_limit_duration = settings.POINT_LIMIT_DURATION 
            t0 = current_semester.records_opening - request.user.student.get_t0_interval()       
            terms = [
            {"name":"T0", "term":t0},
            {"name":"T0 + 24h", "term":t0 + timedelta(days=1)},
            {"name":"T0 + 48h", "term":t0 + timedelta(days=2)},
            {"name":"T0 + 72h", "term":t0 + timedelta(days=3)},
            {"name":"T1", "term":current_semester.records_opening},
            {"name":"T2", "term":current_semester.records_opening + timedelta(days=point_limit_duration)},
            {"name":"T3", "term":current_semester.records_closing},
            ]
        except:
            terms = []
    else:
        terms = []
    
    data = {
        'terms' : terms,
        'zamawiany' : zamawiany,
        'comments' : comments,
        'points' : points,
    }

    return render_to_response('users/my_profile.html', data, context_instance = RequestContext( request ))

@login_required
def employees_list(request, begin = 'A', end='B'):
    if end == 'X':
        end = u'Ż'
        
    employees = Employee.get_list(begin, end)
    semester = Semester.get_current_semester()
    employees = Group.teacher_in_present(employees, semester)

    for e in employees:
        e.short_new = e.user.first_name[:1] + e.user.last_name[:2]
        e.short_old = e.user.first_name[:2] + e.user.last_name[:2]

    if request.is_ajax():
        employees = prepare_ajax_employee_list(employees)
        return AjaxSuccessMessage(message="ok", data=employees)
    else:
        if begin == 'A' and end == 'X':
            char = X
        else:
            char = begin

        data = {
            "employees" : employees,
            "char": char
            }  
    
        return render_to_response('users/employees_list.html', data, context_instance=RequestContext(request))

@login_required
def students_list(request, begin = 'A', end='B'):
    if end == 'X':
        end = u'Ż'

    students = Student.get_list(begin, end)
    students = Record.recorded_students(students)

    if request.is_ajax():
        students = prepare_ajax_students_list(students)
        return AjaxSuccessMessage(message="ok", data=students)
    else:
        if begin == 'A' and end == 'X':
            char = X
        else:
            char = begin
            
        data = { "students" : students, "char": char }
        return render_to_response('users/students_list.html', data, context_instance=RequestContext(request))

@login_required
def logout(request):
    '''logout'''
    logger.info('User %s <id: %s> is logged out ' % (request.user.username, request.user.id))    
    auth.logout(request)
    return HttpResponseRedirect('/')

def login_plus_remember_me(request, *args, **kwargs):
    ''' funkcja logowania uzględniająca zapamiętanie sesji na życzenie użytkownika'''
    if request.method == 'POST':
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(0)
    return login(request, *args, **kwargs)
    
