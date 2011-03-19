# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from apps.enrollment.records.models import *
from apps.enrollment.records.exceptions import *
from apps.users.models import Employee
from datetime import date

DAYS_OF_WEEK = ['poniedziałek','wtorek','środa','czwartek','piątek','sobota','niedziela']
DAYS_SIMPLE= ['poniedzialek', 'wtorek', 'sroda', 'czwartek', 'piatek', 'sobota', 'niedziela']
@login_required
def employeeSchedule(request, schedule_owner=None, delta=None):
    """
        A function returning the schedule of a chosen employee.
    """
    try:
        #choosing correct weekday
        if delta == None:
            delta = 0
        delta = int(delta)%7
        left  = (delta+6)%7
        right = (delta+1)%7
        weekday = (date.today().weekday()+delta+7) % 7
        #choosing user
        if schedule_owner == None :
            owner = request.user
        else :
            owner = Employee.objects.get(user__username=schedule_owner)
        
        #receiving subjects for given weekday
        groups = owner.get_schedule(owner.user.id)
        print groups
        schedule = []
        for group in groups:
            for term in group.terms_:
                if term.day_in_zero_base() == weekday :
                    schedule.append({'group': group,'term':term})

        #sorting by hour of beginning
        schedule.sort(key=lambda student: student['term'].time_from_in_minutes())
        #creating empty entries for formating
        schedule_form = []
        jump = True
        last_time = None
        null = {'group' : 0, 'term': 0}
        for subject in schedule:
            if jump == True :
                jump = False
            else :
                if subject['term'].start_time > last_time :
                    schedule_form.append(null)
                    jump = False
            last_time = subject['term'].end_time
            schedule_form.append(subject)

        data = {
            'schedule': schedule_form,
            'weekday_name': DAYS_OF_WEEK[weekday],
            'left': left,
            'right': right,
            'owner':owner.user,
        }
        return render_to_response('mobile/employee_schedule.html', data, context_instance=RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Użytkownik nie posiada planu bo nie jest studentem.")
        logger.error('User (name = %s) throws NonStudentException on student schedule.' % unicode(schedule_owner) )
        return render_to_response('mobile/error.html', context_instance=RequestContext(request))
    except User.DoesNotExist:
        request.user.message_set.create(message="Użytkownik nie istnieje.")
        logger.error('User (name = %s) throws DoesNotExist on student schedule.' % unicode(schedule_owner) )
        return render_to_response('mobile/error.html', context_instance=RequestContext(request))
        
