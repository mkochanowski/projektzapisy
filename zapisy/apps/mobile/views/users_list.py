# -*- coding: utf-8 -*-

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.http import QueryDict, HttpResponse 
from django.utils import simplejson
from django.db.models import Q 

from apps.users.exceptions import NonUserException, NonEmployeeException, NonStudentException
from apps.users.models import Employee, Student

from apps.users.forms import EmailChangeForm

import logging
logger = logging.getLogger()

KEYNAMES = ['','','ABC','DEF','GHI','JKL','MNO','PQRS','TUV','WXYZ']
        
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
        request.user.message_set.create(message="Nie ma takiego u�ytkownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@login_required
def employeesList(request,key=None):
    employees = Employee.objects.select_related().order_by('user__last_name', 'user__first_name')
    
    if key==None:
        return render_to_response('mobile/keyboard_employees.html', None, context_instance=RequestContext(request))
    
    employees = {
    '2' : employees.filter(Q(user__last_name__startswith='A') | Q(user__last_name__startswith='B') | Q(user__last_name__startswith='C') | Q(user__last_name__startswith='Ć')),
    '3' : employees.filter(Q(user__last_name__startswith='D') | Q(user__last_name__startswith='E') | Q(user__last_name__startswith='F')),
    '4' : employees.filter(Q(user__last_name__startswith='G') | Q(user__last_name__startswith='H') | Q(user__last_name__startswith='I')),
    '5' : employees.filter(Q(user__last_name__startswith='J') | Q(user__last_name__startswith='K') | Q(user__last_name__startswith='L') | Q(user__last_name__startswith='Ł')),
    '6' : employees.filter(Q(user__last_name__startswith='M') | Q(user__last_name__startswith='N') | Q(user__last_name__startswith='O')),
    '7' : employees.filter(Q(user__last_name__startswith='P') | Q(user__last_name__startswith='Q') | Q(user__last_name__startswith='R')| Q(user__last_name__startswith='S') | Q(user__last_name__startswith='Ś')),
    '8' : employees.filter(Q(user__last_name__startswith='T') | Q(user__last_name__startswith='U') | Q(user__last_name__startswith='V')),
    '9' : employees.filter(Q(user__last_name__startswith='W') | Q(user__last_name__startswith='X') | Q(user__last_name__startswith='Y') | Q(user__last_name__startswith='Z') | Q(user__last_name__startswith='Ź') | Q(user__last_name__startswith='Ż')),
    }.get(key, None )
    
    
        
    data = {
            "employees" : employees,
            "keyname" : KEYNAMES[int(key)],
            }  
    
    return render_to_response('mobile/employees_list.html', data, context_instance=RequestContext(request))
    

@login_required
def studentsList(request, key=None):
    students = Student.objects.select_related().order_by('user__last_name', 'user__first_name')

    if key==None:
        return render_to_response('mobile/keyboard_students.html', None, context_instance=RequestContext(request))
        
    students = {
    '2' : students.filter(Q(user__last_name__startswith='A') | Q(user__last_name__startswith='B') | Q(user__last_name__startswith='C') | Q(user__last_name__startswith='Ć')),
    '3' : students.filter(Q(user__last_name__startswith='D') | Q(user__last_name__startswith='E') | Q(user__last_name__startswith='F')),
    '4' : students.filter(Q(user__last_name__startswith='G') | Q(user__last_name__startswith='H') | Q(user__last_name__startswith='I')),
    '5' : students.filter(Q(user__last_name__startswith='J') | Q(user__last_name__startswith='K') | Q(user__last_name__startswith='L') | Q(user__last_name__startswith='Ł')),
    '6' : students.filter(Q(user__last_name__startswith='M') | Q(user__last_name__startswith='N') | Q(user__last_name__startswith='O')),
    '7' : students.filter(Q(user__last_name__startswith='P') | Q(user__last_name__startswith='Q') | Q(user__last_name__startswith='R')| Q(user__last_name__startswith='S') | Q(user__last_name__startswith='Ś')),
    '8' : students.filter(Q(user__last_name__startswith='T') | Q(user__last_name__startswith='U') | Q(user__last_name__startswith='V')),
    '9' : students.filter(Q(user__last_name__startswith='W') | Q(user__last_name__startswith='X') | Q(user__last_name__startswith='Y') | Q(user__last_name__startswith='Z') | Q(user__last_name__startswith='Ź') | Q(user__last_name__startswith='Ż')),
    }.get(key, None )       
    
    
    data = {
            "students" : students,
            "keyname" : KEYNAMES[int(key)],
            }           
            
    return render_to_response('mobile/students_list.html', data, context_instance=RequestContext(request))


