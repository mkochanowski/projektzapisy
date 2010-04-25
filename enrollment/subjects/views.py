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
        
        subject.user_enrolled_to_exercise = Record.is_student_in_subject_group_type(request.user.id, slug, '2')
        subject.user_enrolled_to_laboratory = Record.is_student_in_subject_group_type(request.user.id, slug, '3')
        
        lectures = Record.get_groups_with_records_for_subject(slug, request.user.id, '1')
        exercises = Record.get_groups_with_records_for_subject(slug, request.user.id, '2')
        laboratories = Record.get_groups_with_records_for_subject(slug, request.user.id, '3')
        
        data = {
                'subject' : subject,
                'lectures' : lectures,
                'exercises' : exercises,
                'laboratories' : laboratories,
        }         
        return render_to_response( 'enrollment/subjects/subject.html', data, context_instance = RequestContext( request ) )
    except NonSubjectException:
        request.user.message_set.create(message="Przedmiot nie istnieje.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))

