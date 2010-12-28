# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts               import render_to_response
from django.template                import RequestContext

from django.http import QueryDict, HttpResponse 
from django.utils import simplejson
from django.db.models import Q 

from fereol.enrollment.records.models          import *
from fereol.enrollment.subjects.models         import *
from enrollment.subjects.exceptions import NonSubjectException, NonStudentOptionsException

import logging
logger = logging.getLogger()

def make_it_json_friendly(element):
    element['entity__name'] = unicode(element['entity__name'])
    element['slug'] = unicode(element['slug'])
    return element

@login_required
def subjects(request):
    semesters = Semester.objects.filter(visible=True)

    semesters_list = [(sem.pk, sem.get_name()) for sem in semesters]

    types = Type.get_all_types_of_subjects()
    types_list = [(type.pk, type.name) for type in Type.objects.all()] 

    return render_to_response('enrollment/subjects/subjects_list.html', {'semesters_list' : semesters_list, 'types_list' : types_list}, context_instance=RequestContext(request))

   
@login_required
def subject(request, slug):
    try:
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
        lectures.name = "Wykłady"
        exercises = Record.get_groups_with_records_for_subject(slug, request.user.id, '2')
        laboratories = Record.get_groups_with_records_for_subject(slug, request.user.id, '3')
        exercises_adv = Record.get_groups_with_records_for_subject(slug, request.user.id, '4')
        exer_labs = Record.get_groups_with_records_for_subject(slug, request.user.id, '5')
        seminar = Record.get_groups_with_records_for_subject(slug, request.user.id, '6')
        language = Record.get_groups_with_records_for_subject(slug, request.user.id, '7')
        sport = Record.get_groups_with_records_for_subject(slug, request.user.id, '8')

        tutorials = [lectures, exercises, exercises_adv, laboratories, seminar, exer_labs, language, sport]
                        
        data = {
                'subject' : subject,
                'tutorials' : tutorials,
        }         
        return render_to_response( 'enrollment/subjects/subject.html', data, context_instance = RequestContext( request ) )
    
    except Subject.DoesNotExist, NonSubjectException:
        logger.error('Function subject(slug = %s) throws Subject.DoesNotExist exception.' % unicode(slug) )
        request.user.message_set.create(message="Przedmiot nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

    
@login_required
def list_of_subjects(request):
    semester_name, list_of_types = "", []
    keyword, semester = "", None
    response = Subject.visible.all()      

    try:
        if request.POST.has_key('keyword'):
            keyword = request.POST['keyword']
            response = response.filter(Q(entity__name__icontains=keyword) | Q(teachers__user__last_name__icontains=keyword))

        if request.POST.has_key('semester'):
            semester = request.POST['semester']
            semester_name = Semester.objects.get(id=semester).get_name()
            response = response.filter(semester__id__exact=semester)
        else:
            logger.warning('Function list_of_subjects(request) was called with empty parameter: semester')
       
        if request.POST.has_key('type'):
            list_of_types = request.POST.getlist('type')
            if list_of_types:
               response = response.filter(type__id__in=list_of_types)
        else:
            logger.warning('Function list_of_subjects(request) was called with empty parameter: type')
    
   
    except Semester.DoesNotExist: 
        logger.warning('Function list_of_subjects(request = {%s}) throws Semester.DoesNotExist exception.' % unicode(request.POST) )
        return HttpResponse(simplejson.dumps({'semester_name' : 'nieznany', 'subjects' : {} }), mimetype="application/javascript")
    else:
        response = response.order_by('entity__name').values('id', 'entity__name', 'slug')
    
        response = map(make_it_json_friendly, response)
        result = {'semester_name' : semester_name, 'subjects' : response }

        return HttpResponse(simplejson.dumps(result), mimetype="application/javascript")
 
