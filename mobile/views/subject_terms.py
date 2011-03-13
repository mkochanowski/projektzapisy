# -*- coding: utf-8 -*-
#from django.shortcuts import render_to_response
#from django.template import RequestContext
#from django.contrib.auth.decorators import login_required
#from django.shortcuts import redirect

#from fereol.enrollment.subjects.models import *
#from fereol.enrollment.records.models import Record, Group

from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.shortcuts import redirect
from django.utils import simplejson

from enrollment.subjects.models import *
from users.models import *
from enrollment.records.models import *
from enrollment.records.exceptions import *

from datetime import time
import logging
logger = logging.getLogger()


@login_required
def subjectTerms(request,slug):
    """
        A function returning all groups connected to the chosen subject.
    """
    try:
        #subject = Subject.objects.get(id = slug)
        #sprint subject.slug
        subject = Subject.visible.get(slug=slug)
        try:
            student = request.user.student
            subject.user_enrolled_to_exercise = Record.is_student_in_subject_group_type(request.user.id, slug, '2')
            subject.user_enrolled_to_laboratory = Record.is_student_in_subject_group_type(request.user.id, slug, '3')
            subject.user_enrolled_to_eaoratory = Record.is_student_in_subject_group_type(request.user.id, slug, '4')
            subject.user_enrolled_to_exlaboratory = Record.is_student_in_subject_group_type(request.user.id, slug, '5')
            subject.user_enrolled_to_seminar = Record.is_student_in_subject_group_type(request.user.id, slug, '6')
            subject.user_enrolled_to_langoratory = Record.is_student_in_subject_group_type(request.user.id, slug, '7')
            subject.user_enrolled_to_ssoratory = Record.is_student_in_subject_group_type(request.user.id, slug, '8')
            subject.is_recording_open = subject.is_recording_open_for_student(student)
        except Student.DoesNotExist:
            pass

        lectures = Record.get_groups_with_records_for_subject(slug, request.user.id, '1')
        #lectures = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in lectures]
        exercises = Record.get_groups_with_records_for_subject(slug, request.user.id, '2')
        #exercises = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in exercises]
        laboratories = Record.get_groups_with_records_for_subject(slug, request.user.id, '3')
        #laboratories = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in laboratories]
        exercises_adv = Record.get_groups_with_records_for_subject(slug, request.user.id, '4')
        #exercises_adv = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in exercises_adv]
        exer_labs = Record.get_groups_with_records_for_subject(slug, request.user.id, '5')
        #exer_labs = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in exer_labs]
        seminar = Record.get_groups_with_records_for_subject(slug, request.user.id, '6')
        #seminar = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in seminar]
        language = Record.get_groups_with_records_for_subject(slug, request.user.id, '7')
        #language = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in language]
        sport = Record.get_groups_with_records_for_subject(slug, request.user.id, '8')
        #sport = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in sport]

        data = {
            'subject' : subject,
            'lectures' : lectures,
            'exercises' : exercises,
            'exercises_adv' : exercises_adv,
            'laboratories' : laboratories,
            'seminar' : seminar,
            'exer_labs' : exer_labs,
            'language' : language,
            'sport' : sport
        }
        return render_to_response( 'mobile/subject_terms.html', data, context_instance = RequestContext( request ) )
    except Subject.DoesNotExist, NonSubjectException:
        logger.error('Function subject(slug = %s) throws Subject.DoesNotExist exception.' % unicode(slug) )
        request.user.message_set.create(message="Przedmiot nie istnieje.")
        return render_to_response('mobile/subject_terms.html', context_instance=RequestContext(request))


@login_required
def assign(request,group_id):
    group = Group.objects.get(id=group_id)
    subject = Subject.objects.get(id = group.subject.id)
    try:
        record = Record.add_student_to_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś zapisany do grupy.")
        logger.info('User %s assign to group with id: %d (mobile fereol)' % (request.user,int(group_id)))
        return redirect("subject-terms", slug=subject.slug)
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo nie jesteś studentem.")
        return redirect("subject-terms", slug=subject.slug)
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa nie istnieje.")
        return redirect("subject-terms", slug=subject.slug)
    except AssignedInThisTypeGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać bo jesteś już zapisany do innej grupy tego typu.")
        return redirect("subject-terms", slug=subject.slug)
    except AlreadyAssignedException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo już jesteś zapisany.")
        return redirect("subject-terms", slug=subject.slug)
    except OutOfLimitException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa jest pełna.")
        return redirect("subject-terms", slug=subject.slug)
    except RecordsNotOpenException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo zapisy na ten przedmiot nie sa dla ciebie otwarte.")
        return redirect("subject-terms", slug=subject.slug)
	
@login_required
def resign(request, group_id):
    group = Group.objects.get(id=group_id)
    subject = Subject.objects.get(id = group.subject.id)
    try:
        record = Record.remove_student_from_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś wypisany z grupy.")
        logger.info('User %s resign from group with id: %d (mobile fereol)' % (request.user,int(group_id)))
        return redirect("subject-terms", slug=subject.slug)
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś studentem.")
        return redirect("subject-terms", slug=subject.slug)
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo podana grupa nie istnieje.")
        return redirect("subject-terms", slug=subject.slug)
    except AlreadyNotAssignedException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś zapisany.")
        return redirect("subject-terms", slug=subject.slug)

@login_required
def reassign(request,group_from,group_to):
    try:
        record = Record.change_student_group(request.user.id, group_from, group_to)
        request.user.message_set.create(message="Zostałeś przepisany do innej grupy.")
        logger.info('User %s reassign from group with id: %d to group with id: %d (mobile fereol)' % (request.user,int(group_from),int(group_to)))
        return redirect("subject-terms", slug=record.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz zmienić grupy, bo nie jesteś studentem.")
        return redirect("subject-terms", slug=record.group_slug())
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz zmienić grupy, bo podana grupa nie istnieje.")
        return redirect("subject-terms", slug=record.group_slug())
    except AlreadyNotAssignedException:
        request.user.message_set.create(message="Nie możesz zmienić grupy, bo nie jesteś zapisany.")
        return redirect("subject-terms", slug=record.group_slug())
    except OutOfLimitException:
        request.user.message_set.create(message="Nie możesz się przenieść, bo podana grupa jest pełna.")
        return redirect("subject-terms", slug=record.group_slug())
    except RecordsNotOpenException:
        request.user.message_set.create(message="Nie możesz się przenieść, bo zapisy na ten przedmiot nie sa dla ciebie otwarte.")
        return redirect("subject-terms", slug=record.group_slug())
