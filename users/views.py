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

from users.exceptions import NonUserException, NonEmployeeException, NonStudentException
from users.models import Employee, Student

from users.forms import EmailChangeForm

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
        request.user.message_set.create(message="Nie ma takiego studenta.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
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
        request.user.message_set.create(message="Nie ma takiego pracownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
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
            request.user.message_set.create(message="Twój adres e-mail został zmieniony.")
            return HttpResponseRedirect(reverse('my-profile'))
    else:
        form = EmailChangeForm({'email' : request.user.email})
    return render_to_response('users/email_change_form.html', {'form':form}, context_instance=RequestContext(request))

@login_required  
def password_change_done(request):
    '''informs if password were changed'''
    request.user.message_set.create(message="Twóje hasło zostało zmienione.")
    return HttpResponseRedirect(reverse('my-profile'))
 
@login_required  
def my_profile(request):
    '''profile site'''
    return render_to_response('users/my_profile.html', context_instance = RequestContext( request ))

@login_required
def employees_list(request):
    employees = Employee.objects.all()
    
    data = {
            "employees" : employees,
            }  
    
    return render_to_response('users/employees_list.html', data, context_instance=RequestContext(request))

@login_required
def students_list(request):
    students = Student.objects.all()
    data = {
            "students" : students,
            }  
    return render_to_response('users/students_list.html', data, context_instance=RequestContext(request))

@login_required
def logout(request):
    '''logout'''
    auth.logout(request)
    return HttpResponseRedirect('/')
