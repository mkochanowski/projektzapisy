# -*- coding: utf-8 -*-

from django.contrib import auth, messages
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
from apps.enrollment.courses.exceptions import MoreThanOneCurrentSemesterException                                 
from apps.users.utils import prepare_ajax_students_list,\
                             prepare_ajax_employee_list

from apps.users.models import Employee, Student, BaseUser
from apps.enrollment.courses.models import Semester, Group
from apps.enrollment.records.models import Record

from apps.users.forms import EmailChangeForm, BankAccountChangeForm, ConsultationsChangeForm

from datetime import timedelta
from libs.ajax_messages import AjaxFailureMessage, AjaxSuccessMessage
import datetime

import logging
logger = logging.getLogger()
import vobject
from apps.enrollment.courses.models.group import GROUP_TYPE_CHOICES


GTC = {'1' : 'wy', '2': 'cw', '3': 'pr',
        '4': 'cw', '5': 'cw+prac',
        '6': 'sem', '7': 'lek', '8': 'WF',
        '9': 'rep', '10': 'proj'}


@login_required
def student_profile(request, user_id):
    """student profile"""
    try:
        student = User.objects.get(id=user_id).student
        groups = Student.get_schedule(student)

        data = {
                'groups' : groups,
                'student' : student,
            }

        if request.is_ajax():
            return render_to_response('users/ajax_student_profile.html', data, context_instance=RequestContext(request))
        else:
            begin = student.user.last_name[0]
            students = Student.get_list(begin)
            students = Record.recorded_students(students)
            data['students'] = students
            data['char']     = begin
            return render_to_response('users/student_profile.html', data, context_instance=RequestContext(request))

    except Student.DoesNotExist:
        logger.error('Function student_profile(id = %d) throws NonStudentException while acessing to non existing student.' % int(user_id) )
        request.user.message_set.create(message="Nie ma takiego studenta.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
        logger.error('Function student_profile(id = %d) throws User.DoesNotExist while acessing to non existing user.' % int(user_id) )
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
        if request.is_ajax():
            return render_to_response('users/ajax_employee_profile.html', data, context_instance=RequestContext(request))
        else:
            begin = user.last_name[0]
            employees = Employee.get_list(begin)
            semester = Semester.get_current_semester()
            employees = Group.teacher_in_present(employees, semester)

            for e in employees:
                e.short_new = e.user.first_name[:1] + e.user.last_name[:2]
                e.short_old = e.user.first_name[:2] + e.user.last_name[:2]

            data['employees'] = employees
            data['char'] = begin
              
            return render_to_response('users/employee_profile.html', data, context_instance=RequestContext(request))
        
    except Employee.DoesNotExist:
        logger.error('Function employee_profile(user_id = %d) throws NonEmployeeException while acessing to non existing employee.' % int(user_id) )
        request.user.message_set.create(message="Nie ma takiego pracownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
        logger.error('Function employee_profile(id = %d) throws User.DoesNotExist while acessing to non existing user.' % int(user_id) )
        request.user.message_set.create(message="Nie ma takiego użytkownika.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except MoreThanOneCurrentSemesterException:
        data = {'employee' : employee}
        logger.error('Function employee_profile throws MoreThanOneCurrentSemesterException.' )
        request.user.message_set.create(message="Przepraszamy, system jest obecnie nieaktywny z powodu niewłaściwej konfiguracji semestrów. Prosimy spróbować później.")
        return render_to_response('users/employee_profile.html', data, context_instance=RequestContext(request))
    
@login_required
def email_change(request):
    '''function that enables mail changing'''
    if request.POST:
        data = request.POST.copy()
        form = EmailChangeForm(data, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']

            user = User.objects.filter(email=email)

            if user and user <> request.user:
                messages.error(request, "Podany adres jest już przypisany do innego użytkownika!")
                return render_to_response('users/email_change_form.html', {'form':form}, context_instance=RequestContext(request))

            form.save()
            logger.info('User (%s) changed email' % request.user.get_full_name())
            messages.success(request, message="Twój adres e-mail został zmieniony.")
            return HttpResponseRedirect(reverse('my-profile'))
    else:
        form = EmailChangeForm({'email' : request.user.email})
    return render_to_response('users/email_change_form.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def bank_account_change(request):
    '''function that enables bank account changing'''
    if request.POST:
        data = request.POST.copy()
        zamawiany = Student.get_zamawiany(request.user.id)
        form = BankAccountChangeForm(data, instance=zamawiany)
        if form.is_valid():
            form.save()
            logger.info('User (%s) changed bank account' % request.user.get_full_name())
            request.user.message_set.create(message="Twój numer konta bankowego został zmieniony.")
            return HttpResponseRedirect(reverse('my-profile'))
    else:
        zamawiany = Student.get_zamawiany(request.user.id)
        form = BankAccountChangeForm({'bank_account': zamawiany.bank_account})
    return render_to_response('users/bank_account_change_form.html', {'form':form}, context_instance=RequestContext(request))

@login_required
def consultations_change(request):
    '''function that enables consultations changing'''
    try:
        employee = request.user.employee     
        if request.POST:
            data = request.POST.copy()
            form = ConsultationsChangeForm(data, instance=employee)
            if form.is_valid():
                form.save()
                logger.info('User (%s) changed consultations' % request.user.get_full_name())
                request.user.message_set.create(message="Twoje dane zostały zmienione.")
                return HttpResponseRedirect(reverse('my-profile'))
        else:
            zamawiany = Student.get_zamawiany(request.user.id)
            form = ConsultationsChangeForm({'consultations': employee.consultations, 'homepage': employee.homepage, 'room': employee.room})
        return render_to_response('users/consultations_change_form.html', {'form':form}, context_instance=RequestContext(request))
    except Employee.DoesNotExist:
        request.user.message_set.create(message='Nie jesteś pracownikiem.')
        return render_to_response('common/error.html', \
                context_instance=RequestContext(request))

@login_required  
def password_change_done(request):
    '''informs if password were changed'''
    logger.info('User (%s) changed password' % request.user.get_full_name())
    request.user.message_set.create(message="Twoje hasło zostało zmienione.")
    return HttpResponseRedirect(reverse('my-profile'))

@login_required  
def my_profile(request):
    '''profile site'''
    logger.info('User %s <id: %s> is logged in ' % (request.user.username, request.user.id))
    current_semester = Semester.get_default_semester()
    zamawiany = Student.get_zamawiany(request.user.id)
    comments = zamawiany and zamawiany.comments or ''
    points = zamawiany and zamawiany.points or 0
    try:
        consultations = request.user.employee.consultations
        room = request.user.employee.room
        homepage = request.user.employee.homepage
        room = room and room or ''
        homepage = homepage and homepage or ''
    except Employee.DoesNotExist:
        consultations = ''
        homepage = ''
        room = ''
    if current_semester:
        try:

            point_limit_duration = settings.ECTS_LIMIT_DURATION
            t0 = current_semester.records_opening - request.user.student.get_t0_interval()       
            terms = [
            {"name":"T0", "term":t0},
            {"name":"T0 + 24h", "term":t0 + timedelta(days=1)},
            {"name":"T0 + 48h", "term":t0 + timedelta(days=2)},
            {"name":"T0 + 72h", "term":t0 + timedelta(days=3)},
            {"name":"Zniesienie limitu 40 ECTS", "term":current_semester.records_opening + timedelta(days=point_limit_duration)},
            {"name":"Koniec zapisów", "term":current_semester.records_closing},
            ]
        except KeyError:
            terms = []
    else:
        terms = []
    
    data = {
        'terms' : terms,
        'zamawiany' : zamawiany,
        'comments' : comments,
        'points' : points,
        'consultations' : consultations,
        'room' : room,
        'homepage' : homepage
    }

    return render_to_response('users/my_profile.html', data, context_instance = RequestContext( request ))

def employees_list(request, begin = 'A'):

    employees = Employee.get_list(begin)
    try:
        semester = Semester.get_current_semester()
        employees = Group.teacher_in_present(employees, semester)
    except MoreThanOneCurrentSemesterException:
        logger.error('Function employee_list throws MoreThanOneCurrentSemesterException.' )
        request.user.message_set.create(message="Przepraszamy, system jest obecnie nieaktywny z powodu niewłaściwej konfiguracji semestrów. Prosimy spróbować później.")
        employees = Employee.objects.all()

    for e in employees:
        e.short_new = e.user.first_name[:1] + e.user.last_name[:2]
        e.short_old = e.user.first_name[:2] + e.user.last_name[:2]

    if request.is_ajax():
        employees = prepare_ajax_employee_list(employees)
        return AjaxSuccessMessage(message="ok", data=employees)
    else:
        data = {
            "employees" : employees,
            "char": begin
            }  
    
        return render_to_response('users/employees_list.html', data, context_instance=RequestContext(request))

def consultations_list(request, begin='A'):

    employees = Employee.get_list('All')
    semester = Semester.get_current_semester()
    employees = Group.teacher_in_present(employees, semester)

    if request.is_ajax():
        employees = prepare_ajax_employee_list(employees)
        return AjaxSuccessMessage(message="ok", data=employees)
    else:
        data = {
            "employees" : employees,
            "char": begin
            }          
        return render_to_response('users/consultations_list.html', data, context_instance=RequestContext(request))


@login_required
def students_list(request, begin = 'A'):
    students = Student.get_list(begin)
    students = Record.recorded_students(students)

    if request.is_ajax():
        students = prepare_ajax_students_list(students)
        return AjaxSuccessMessage(message="ok", data=students)
    else:
        data = { 
            "students" : students, 
            "char": begin
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
    
@login_required
def create_ical_file(request):
    user = request.user
    user_id = user.id
    user_full_name = user.get_full_name()
    semester = Semester.get_default_semester()
    semester_beginning = semester.semester_beginning
    semester_beginning_weekday = semester_beginning.weekday() + 1
    semester_ending = semester.semester_ending
    until = semester_ending.strftime("%Y%m%dT235959Z")
    
    
    cal = vobject.iCalendar()
    cal.add('x-wr-timezone').value = 'Europe/Warsaw'
    cal.add('version').value = '2.0'
    cal.add('prodid').value = 'Fereol'
    cal.add('calscale').value = 'GREGORIAN'
    cal.add('calname').value = user_full_name + ' - schedule'
    cal.add('method').value = 'PUBLISH'

    groups_employee = []
    groups_student = []
    try:
        user.student
        groups_student = filter(lambda x: x.course.semester==semester, Record.get_groups_for_student(user_id))
    except Student.DoesNotExist:
        pass
    try:
        user.employee
        groups_employee = map(lambda x: x, Group.objects.filter(course__semester = semester, teacher = user.employee))
    except Employee.DoesNotExist:
        pass
    groups = groups_employee + groups_student
    for group in groups:
        course_name = group.course.name
        group_type = GTC[group.type]
        try:
            terms = group.get_all_terms()
        except IndexError:
            continue
        for term in terms:
            start_time = term.start_time
            end_time = term.end_time
            weekday = int(term.dayOfWeek)
            classroom_number = term.classroom.number
    
            diff = semester_beginning_weekday - weekday
            if diff<0:
                diff += 7
            diff = 7 - diff
            start_date = semester_beginning + datetime.timedelta(days=diff)
            start_datetime = datetime.datetime.combine(start_date, start_time)
            end_datetime = datetime.datetime.combine(start_date, end_time)
    
            event = cal.add('vevent')
            event.add('summary').value = '%s, %s, s.%s' % (course_name,group_type,classroom_number)
            event.add('dtstart').value  = start_datetime
            event.add('dtend').value = end_datetime
            event.add('rrule').value = "FREQ=WEEKLY;UNTIL=%s" % (until,)

    cal_str = cal.serialize()
    response = HttpResponse(cal_str, content_type='application/calendar')
    response['Content-Disposition'] = 'attachment; filename=schedule.ical'
    return response    
