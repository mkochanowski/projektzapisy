# -*- coding: utf-8 -*-
#from django.shortcuts import render_to_response
#from django.template import RequestContext
#from django.contrib.auth.decorators import login_required
#from django.shortcuts import redirect

#from apps.enrollment.courses.models import *
#from apps.enrollment.records.models import Record, Group

from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.shortcuts import redirect
from django.utils import simplejson

from apps.enrollment.courses.models import *
from apps.users.models import *
from apps.enrollment.records.models import *
from apps.enrollment.records.exceptions import *

from datetime import time
import logging
logger = logging.getLogger()


@login_required
def courseTerms(request,slug):
    """
        A function returning all groups connected to the chosen course.
    """
    try:
        #course = Course.objects.get(id = slug)
        #sprint course.slug
        course = Course.visible.get(slug=slug)
        try:
            student = request.user.student
            course.user_enrolled_to_exercise = Record.is_student_in_course_group_type(request.user, slug, '2')
            course.user_enrolled_to_laboratory = Record.is_student_in_course_group_type(request.user, slug, '3')
            course.user_enrolled_to_eaoratory = Record.is_student_in_course_group_type(request.user, slug, '4')
            course.user_enrolled_to_exlaboratory = Record.is_student_in_course_group_type(request.user, slug, '5')
            course.user_enrolled_to_seminar = Record.is_student_in_course_group_type(request.user, slug, '6')
            course.user_enrolled_to_langoratory = Record.is_student_in_course_group_type(request.user, slug, '7')
            course.user_enrolled_to_ssoratory = Record.is_student_in_course_group_type(request.user, slug, '8')
            course.is_recording_open = course.is_recording_open_for_student(student)
        except Student.DoesNotExist:
            pass

        lectures = Record.get_groups_with_records_for_course(slug, request.user.id, '1')
        #lectures = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in lectures]
        exercises = Record.get_groups_with_records_for_course(slug, request.user.id, '2')
        #exercises = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in exercises]
        laboratories = Record.get_groups_with_records_for_course(slug, request.user.id, '3')
        #laboratories = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in laboratories]
        exercises_adv = Record.get_groups_with_records_for_course(slug, request.user.id, '4')
        #exercises_adv = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in exercises_adv]
        exer_labs = Record.get_groups_with_records_for_course(slug, request.user.id, '5')
        #exer_labs = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in exer_labs]
        seminar = Record.get_groups_with_records_for_course(slug, request.user.id, '6')
        #seminar = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in seminar]
        language = Record.get_groups_with_records_for_course(slug, request.user.id, '7')
        #language = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in language]
        sport = Record.get_groups_with_records_for_course(slug, request.user.id, '8')
        #sport = [{'group': x, 'limit':x.limit, 'enrolled':Record.number_of_students(x)} for x in sport]

        data = {
            'course' : course,
            'lectures' : lectures,
            'exercises' : exercises,
            'exercises_adv' : exercises_adv,
            'laboratories' : laboratories,
            'seminar' : seminar,
            'exer_labs' : exer_labs,
            'language' : language,
            'sport' : sport
        }
        return render_to_response( 'mobile/course_terms.html', data, context_instance = RequestContext( request ) )
    except Course.DoesNotExist, NonCourseException:
        logger.error('Function course(slug = %s) throws Course.DoesNotExist exception.' % unicode(slug) )
        request.user.message_set.create(message="Przedmiot nie istnieje.")
        return render_to_response('mobile/course_terms.html', context_instance=RequestContext(request))
