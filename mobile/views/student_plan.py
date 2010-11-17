# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from enrollment.records.models import *
from enrollment.records.exceptions import *
from datetime import date

DAYS_OF_WEEK = ['poniedziałek','wtorek','środa','czwartek','piątek','sobota','niedziela']

@login_required
def studentPlan(request, delta=0):
    """
        Main page
    """
    try:
        #obsluga dni tygodnia
        delta = int(delta) % 7
        today = date.today()
        weekday = (today.weekday()+delta+7) % 7
        weekday_name = DAYS_OF_WEEK[weekday]
        left  = (delta+6)%7
        right = (delta+1)%7
        groups = Record.get_student_all_detiled_enrollings(request.user.id)
        subjects = []
        for group in groups:
            for term in group.terms_:
                if term.day_in_zero_base() == weekday :
                    subjects.append({'group': group,'term':term})
        #tutaj przefiltrować grupy na dany dzień tygodnia (dzisiejszy albo przekazany?)
        data = {
            'groups': groups,
            'subjects': subjects,
            'weekday_name': weekday_name,
            'left': left,
            'right': right,
        }
        return render_to_response('mobile/student_plan.html', data, context_instance=RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Nie masz planu, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
        
