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

from users.exceptions import NonUserException, NonEmployeeException, NonStudentException
from users.models import Employee, Student
from enrollment.subjects.models import Semester

from users.forms import EmailChangeForm

from datetime import timedelta
import datetime

import logging
logger = logging.getLogger()

def student_profile(request, user_id):
    """student profile"""
    try:
        user = User.objects.get(id=user_id)
        student = user.student
        groups = Student.get_schedule(user.id)

        data = {
	            'groups' : groups,
	            'student' : student,
	        }

        return render_to_response('users/student_profile.html', data, context_instance=RequestContext(request))

    except NonStudentException:
        logger.error('Function student_profile(id = %d) throws NonStudentException while acessing to non existing student.' % user_id )
        request.user.message_set.create(message="Nie ma takiego studenta.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
        logger.error('Function student_profile(id = %d) throws User.DoesNotExist while acessing to non existing user.' % user_id )
        request.user.message_set.create(message="Nie ma takiego użytkownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
        
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
    if current_semester:
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
    else:
        terms = []
    
    data = {
        'terms' : terms,
    }

    return render_to_response('users/my_profile.html', data, context_instance = RequestContext( request ))

@login_required
def employees_list(request):
    employees = Employee.objects.select_related().order_by('user__last_name', 'user__first_name')
    
    data = {
            "employees" : employees,
            }  
    
    return render_to_response('users/employees_list.html', data, context_instance=RequestContext(request))

@login_required
def students_list(request):
    students = Student.objects.select_related().order_by('user__last_name', 'user__first_name')
    data = {
            "students" : students,
            }  
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
    
