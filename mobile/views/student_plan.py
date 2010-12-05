# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from enrollment.records.models import *
from enrollment.records.exceptions import *
from datetime import date

DAYS_OF_WEEK = ['poniedziałek','wtorek','środa','czwartek','piątek','sobota','niedziela']

@login_required
def studentPlan(request, gosciu=0, delta=0):
    """
        Main page
    """
    try:
        #choosing correct weekday
        delta = int(delta)%7
        left  = (delta+6)%7
        right = (delta+1)%7
        weekday = (date.today().weekday()+delta+7) % 7
        if gosciu == 0 :
            ruser = request.user
        else :
            ruser = User.objects.get(username=gosciu)
            
        #receiving subjects for given weekday
        groups = Record.get_student_all_detiled_enrollings(ruser.id)
        subjects = []
        for group in groups:
            for term in group.terms_:
                if term.day_in_zero_base() == weekday :
                    subjects.append({'group': group,'term':term})

        #sorting by hour of beginning
        subjects.sort(key=lambda student: student['term'].time_from_in_minutes())
        #creating empty entries for formating
        subjects_form = []
        jump = True
        last_time = None
        null = {'group' : 0, 'term': 0}
        for subject in subjects:
            if jump == True :
                jump = False
            else :
                if subject['term'].start_time > last_time :
                    subjects_form.append(null)
                    jump = False
            last_time = subject['term'].end_time
            subjects_form.append(subject)

        data = {
            'subjects': subjects_form,
            'weekday_name': DAYS_OF_WEEK[weekday],
            'left': left,
            'right': right,
            'ruser':ruser.username,
        }
        return render_to_response('mobile/student_plan.html', data, context_instance=RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Nie jesteś studentem lub nie wybrałeś poprawnego numeru indeksu.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
        
