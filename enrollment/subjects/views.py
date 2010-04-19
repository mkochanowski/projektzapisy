# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.template                import RequestContext

from fereol.enrollment.records.models          import *
from fereol.enrollment.subjects.models         import *
from exceptions import NonSubjectException

@login_required
def subjects(request):
    subjects = Subject.objects.all()
    return render_to_response( 'enrollment/subjects/subjects_list.html', { 'subjects' : subjects } )

@login_required
def subject( request, slug ):
    try:
        subject = Subject.objects.get(slug=slug)
        lectures = Group.get_groups_for_subject(slug, 1) 
        exercises = Group.get_groups_for_subject(slug, 2)
        laboratories = Group.get_groups_for_subject(slug, 3)

        user_groups = Record.get_groups_for_student(request.user.id)
        
        for lec in lectures:
            if lec in user_groups:
                lec.signed = True
            lec.enrolled = Record.number_of_students(group = lec)
    
        for exe in exercises:
            if exe in user_groups:
                exe.signed = True
            exe.enrolled = Record.number_of_students(group = exe)
    
        for lab in laboratories:
            if lab in user_groups:
                lab.signed = True
            lab.enrolled = Record.number_of_students(group = lab)
        
        data = {
                'subject' : subject,
                'lectures' : lectures,
                'exercises' : exercises,
                'laboratories' : laboratories,
        }         
        return render_to_response( 'enrollment/subjects/subject.html', data, context_instance = RequestContext( request ) )
    except NonSubjectException:
        request.user.message_set.create(message="Przedmiot nie istnieje.")
        # trzeba dodac redirecta

