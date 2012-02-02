# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.utils import simplejson
from django.views.decorators.http import require_POST
from django.utils.datastructures import MultiValueDictKeyError
from django.db import transaction
from django.core.cache import cache as mcache

from debug_toolbar.panels.timer import TimerDebugPanel
from apps.enrollment.courses.models import *
from apps.users.models import *
from apps.enrollment.records.models import *
from apps.enrollment.records.exceptions import *
from apps.enrollment.courses.views import prepare_courses_list_to_render
from apps.enrollment.records.utils import *

from libs.ajax_messages import *

@require_POST
@transaction.commit_on_success
def prototype_set_pinned(request):
    '''
        Response for AJAX query for pinning or un-pinning group from student's
        schedule.
    '''
    if not request.user.is_authenticated():
        return AjaxFailureMessage('NotAuthenticated', 'Nie jesteś zalogowany.')

    try:
        group_id = int(request.POST['group'])
        set_pinned = request.POST['pin'] == 'true'
    except MultiValueDictKeyError:
        return AjaxFailureMessage('InvalidRequest', 'Nieprawidłowe zapytanie.')

    try:
        if set_pinned:
            Record.pin_student_to_group(request.user.id, group_id)
            return AjaxSuccessMessage(\
                'Grupa została przypięta do Twojego planu.')
        else:
            Record.unpin_student_from_group(request.user.id, group_id)
            return AjaxSuccessMessage('Grupa została odpięta od Twojego planu.')
    except NonStudentException:
        transaction.rollback()
        return AjaxFailureMessage('NonStudent', \
            'Nie możesz przypinać grup do planu, bo nie jesteś studentem.');
    except NonGroupException:
        transaction.rollback()
        return AjaxFailureMessage('NonGroup', \
            'Nie możesz przypiąć tej grupy, bo już nie istnieje.');
    except AlreadyPinnedException:
        transaction.rollback()
        return AjaxSuccessMessage( \
            'Grupa jest już przypięta do Twojego planu.');
    except AlreadyNotPinnedException:
        transaction.rollback()
        return AjaxSuccessMessage( \
            'Grupa jest już odpięta od Twojego planu.');

@require_POST
@transaction.commit_on_success
def set_enrolled(request, method):
    '''
        Set student assigned (or not) to group.
    '''
    is_ajax = (method == '.json')
    message_context = None if is_ajax else request

    if not request.user.is_authenticated():
        return AjaxFailureMessage.auto_render('NotAuthenticated', \
            'Nie jesteś zalogowany.', message_context)

    try:
        group_id = int(request.POST['group'])
        set_enrolled = request.POST['enroll'] == 'true'
    except MultiValueDictKeyError:
        return AjaxFailureMessage.auto_render('InvalidRequest', \
            'Nieprawidłowe zapytanie.', message_context)

    if request.user.student.block:
        return AjaxFailureMessage.auto_render('ScheduleLocked', \
            'Twój plan jest zablokowany.', message_context);
    student = request.user.student

    logger.info('User %s <id: %s> set himself %s to group with id: %s' % \
        (request.user.username, request.user.id, \
        ('enrolled' if set_enrolled else 'not enrolled'), group_id))

    def prepare_group_data(course, student):
        groups = course.groups.all()
        queued = Queue.queued.filter(group__course=course, student=student)
        enrolled_ids = Record.enrolled.filter(group__course=course, \
            student=student).values_list('group__id', flat=True)
        queued_ids = queued.values_list('group__id', flat=True)
        pinned_ids = Record.pinned.filter(group__course=course, \
            student=student).values_list('group__id', flat=True)
        queue_priorities = Queue.queue_priorities_map(queued)

        data = {}
        for group in groups:
            data[group.id] = simplejson.dumps(group.serialize_for_ajax(
                enrolled_ids, queued_ids, pinned_ids,
                queue_priorities, student))
        return data

    try:
        group = Group.objects.get(id=group_id)
        if set_enrolled:
            moved = Record.is_student_in_course_group_type(\
                user=request.user, slug=group.course_slug(),\
                group_type=group.type) #TODO: omg ale crap
            connected_records = Record.add_student_to_group(request.user, group)
            record = connected_records[0]
            if moved:
                message = 'Zostałeś przeniesiony do wybranej grupy.'
            elif len(connected_records) == 1:
                message = 'Zostałeś zapisany do wybranej grupy.'
            else:
                message = 'Zostałeś zapisany do wybranej grupy oraz grup ' + \
                'powiązanych.'
        else:
            connected_records = None
            record = Record.remove_student_from_group(request.user, group)
            message = 'Zostałeś wypisany z wybranej grupy.'

        if is_ajax:
            return AjaxSuccessMessage(message,
                prepare_group_data(group.course, student))
        else:
            request.user.message_set.create(message=message)
            return redirect('course-page', slug=record.group_slug())
    except NonStudentException:
        transaction.rollback()
        return AjaxFailureMessage.auto_render('NonStudent',
            'Nie możesz zapisać lub wypisać się z grupy, ponieważ nie jesteś' +\
            ' studentem.', message_context)
    except NonGroupException:
        transaction.rollback()
        return AjaxFailureMessage.auto_render('NonGroup',
            'Nie możesz zapisać lub wypisać się z grupy, ponieważ ona już' +\
            ' nie istnieje.', message_context)
    except AlreadyAssignedException:
        message = 'Jesteś już zapisany do tej grupy.'
        if is_ajax:
            return AjaxSuccessMessage(message,
                prepare_group_data(group.course, student))
        else:
            request.user.message_set.create(message=message)
            return redirect('course-page', slug=Group.objects.\
                get(id=group_id).course_slug())
    except AlreadyNotAssignedException:
        try:
            Queue.remove_student_from_queue(request.user.id, group_id)
            message = 'Zostałeś wypisany z kolejki wybranej grupy.'
        except AlreadyNotAssignedException:
            message = 'Jesteś już wypisany z tej grupy.'
        if is_ajax:
            return AjaxSuccessMessage(message,
                prepare_group_data(group.course, student))
        else:
            request.user.message_set.create(message=message)
            return redirect('course-page', slug=Group.objects.\
                get(id=group_id).course_slug())
    except OutOfLimitException:
        try:
            Queue.add_student_to_queue(request.user.id, group_id)
            try:
                Record.unpin_student_from_group(request.user.id, group_id)
            except AlreadyNotPinnedException:
                pass
            message = 'Grupa jest pełna. Zostałeś zapisany do kolejki.'
            if is_ajax:
                return AjaxFailureMessage.auto_render('Queued', message,\
                    message_context, prepare_group_data(group.course, student))
            else:
                request.user.message_set.create(message=message)
                return redirect('course-page', slug=Group.objects.\
                    get(id=group_id).course_slug())
        except AlreadyQueuedException:
            return AjaxFailureMessage.auto_render('AlreadyQueued',
                'Jesteś już zapisany do kolejki.', \
                message_context)
    except RecordsNotOpenException:
        transaction.rollback()
        if set_enrolled:
            message = 'Nie możesz się zapisać, ponieważ zapisy na ten ' + \
                'przedmiot nie są dla Ciebie otwarte.'
        else:
            message = 'Nie możesz się wypisać, ponieważ zapisy są już ' + \
                'zamknięte.'
        return AjaxFailureMessage.auto_render('RecordsNotOpen', message, \
            message_context)
    except ECTS_Limit_Exception:
        if is_ajax:
            return AjaxFailureMessage.auto_render('ECTSLimit', 'Przekroczyłeś limit ECTS')
        else:
            messages.error(request, 'Przekroczony limit 40 ECTS')
            return redirect('course-page', slug=Group.objects.\
                    get(id=group_id).course_slug())
    except InactiveStudentException:
        message = 'Nie możesz się zapisać, ponieważ nie jesteś aktywnym ' + \
            'studentem.'
        if is_ajax:
            return AjaxFailureMessage.auto_render('InactiveStudent', message, \
                message_context)
        else:
            messages.error(request, message)
            return redirect('course-page', slug=Group.objects.\
                    get(id=group_id).course_slug())


@require_POST
def records_set_locked(request, method):
    '''
        Locks or unlocks records for student to prevent mistakes.
    '''
    is_ajax = (method == '.json')
    message_context = None if is_ajax else request

    if not request.user.is_authenticated():
        return AjaxFailureMessage.auto_render('NotAuthenticated',\
            'Nie jesteś zalogowany.', message_context)

    try:
        lock = request.POST['lock'] == 'true'
    except MultiValueDictKeyError:
        return AjaxFailureMessage.auto_render('InvalidRequest',\
            'Nieprawidłowe zapytanie.', message_context)

    try:
        logger.info('User %s  <id: %d> %s his/her records' %\
            (request.user.username, request.user.id,\
            ('locks' if lock else 'unlocks')))
        request.user.student.records_set_locked(lock)

        message = 'Plan został ' + ('zablokowany.' if lock else ' odblokowany.')
        if is_ajax:
            return AjaxSuccessMessage(message)
        else:
            request.user.message_set.create(message=message)
            return redirect('schedule-prototype')
    except Student.DoesNotExist:
        transaction.rollback()
        return AjaxFailureMessage.auto_render('NonStudent',\
            'Nie jesteś studentem.', message_context)

@require_POST
@login_required
@transaction.commit_on_success
def set_queue_priority(request, method):
    '''
        Sets new priority for queue of some group
    '''
    is_ajax = (method == '.json')
    message_context = None if is_ajax else request

    try:
        group_id = int(request.POST['id'])
        priority = int(request.POST['priority'])
    except MultiValueDictKeyError:
        return AjaxFailureMessage.auto_render('InvalidRequest',\
            'Nieprawidłowe zapytanie.', message_context)

    try:
        if request.user.student.block:
            return AjaxFailureMessage.auto_render('ScheduleLocked', \
                'Twój plan jest zablokowany.', message_context);

        queue = Queue.objects.get(student=request.user.student, group__id=group_id).select_related('group')
        priority = int(priority)
        if priority > settings.QUEUE_PRIORITY_LIMIT or priority < 1:
            return AjaxFailureMessage.auto_render('FatalError', \
                'Nieprawidłowa wartość priorytetu.', message_context);
        if queue.priority != priority:
            queue.set_priority(priority)
        if is_ajax:
            return AjaxSuccessMessage()
        else:
            return redirect("course-page", slug=queue.group_slug())
    except Queue.DoesNotExist:
        transaction.rollback()
        return AjaxFailureMessage.auto_render('NotQueued',\
            'Nie jesteś w kolejce do tej grupy.', message_context)

@login_required
def records(request, group_id):
    '''
        Group records view - list of all students enrolled and queued to group.
    '''
    try:
        group = Group.objects.get(id=group_id)
        students_in_group = Record.get_students_in_group(group_id)
        students_in_queue = Queue.get_students_in_queue(group_id)
        all_students = Student.objects.all()
        data = prepare_courses_list_to_render(request)
        data.update({
            'all_students' : all_students,
            'students_in_group' : students_in_group,
            'students_in_queue' : students_in_queue,
            'group' : group,
        })
        return render_to_response('enrollment/records/records_list.html', data,
            context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Podana grupa nie istnieje.")
        return render_to_response('common/error.html',\
            context_instance=RequestContext(request))

@login_required
def own(request):
    ''' own schedule view '''

    default_semester = Semester.get_default_semester()
    if not default_semester:
        raise RuntimeError('Brak aktywnego semestru')

    try:
        student = request.user.student
    except Student.DoesNotExist:
        student = None
        try:
            employee = request.user.employee
        except Employee.DoesNotExist:
            employee = None
    if student is None and employee is None:
        request.user.message_set.create(message = \
            'Nie jesteś pracownikiem ani studentem.')
        return render_to_response('common/error.html', \
            context_instance=RequestContext(request))

    if student:
        courses = prepare_schedule_courses(request, for_student=student)
    elif employee:
        courses = prepare_schedule_courses(request, for_employee=employee)

    data = prepare_schedule_data(request, courses)

    if student:
        course_objects = map(lambda course: course['object'], courses)
        points = Course.get_points_for_courses(course_objects, student.program)
        points_sum = reduce(lambda sum, k: sum + points[k].value, points, 0)  
        points_type = student.program.type_of_points 
        data.update({
            'points': points,
            'points_type': points_type,
            'points_sum': points_sum
        })

    data.update({
        'courses': courses,
    })

    return render_to_response('enrollment/records/schedule.html',\
        data, context_instance = RequestContext(request))

@login_required       
def schedule_prototype(request):
    ''' schedule prototype view '''
    try:
        student = request.user.student
    except Student.DoesNotExist:
        request.user.message_set.create(message='Nie jesteś studentem.')
        return render_to_response('common/error.html', \
            context_instance=RequestContext(request))

    TimerDebugPanel.timer_start('loading_semester', 'Pobieranie semestru')
    default_semester = Semester.get_default_semester()
    if not default_semester:
        request.user.message_set.create(message='Brak aktywnego semestru.')
        data = {
            'student_records': [],
            'courses' : [],
            'semester' : 'nieokreślony',
            'types_list' : []
        }
        return render_to_response('enrollment/records/schedule_prototype.html',\
            data, context_instance = RequestContext(request))
    TimerDebugPanel.timer_stop('loading_semester')

    TimerDebugPanel.timer_start('preload_cache', \
        'Przygotowywanie cache StudentOptions')
    StudentOptions.preload_cache(student, default_semester)
    TimerDebugPanel.timer_stop('preload_cache')

    TimerDebugPanel.timer_start('data_prepare', 'Przygotowywanie danych')    
    cached_courses = mcache.get("schedule_prototype_courses_%s_%s" % (default_semester.id, student.id), 'DoesNotExist')
    if cached_courses == 'DoesNotExist':
        """
        was_enroled_sql = 'SELECT COUNT(*) FROM "records_record"' \
                                ' INNER JOIN "courses_group" ON ("records_record"."group_id" = "courses_group"."id")' \
                                ' INNER JOIN "courses_course" cc ON ("courses_group"."course_id" = cc."id")' \
                                ' WHERE (cc."entity_id" = "courses_course"."entity_id"  AND "records_record"."student_id" = '+ str(student.id)+ '' \
                                ' AND "records_record"."status" = \'1\' AND "cc"."semester_id" <> "courses_course"."semester_id")'
        """
        terms = Term.get_all_in_semester(default_semester )
#                    .extra(select={'was_enro'})
        courses = prepare_courses_with_terms( terms )
        for course in courses:
            course['info'].update({
                'is_recording_open': course['object'].\
                    is_recording_open_for_student(student),
                #TODO: kod w prepare_courses_list_to_render moim zdaniem nie
                #      zadziała
                'was_enrolled': 'False',
	        'english': course['object'].english,
	        'exam': course['object'].exam,
	        'suggested_for_first_year': course['object'].suggested_for_first_year,
            })
            for term in course['terms']:
                term.update({ # TODO: do szablonu
                    'json': simplejson.dumps(term['info'])
                })
        cached_courses = courses
        mcache.set("schedule_prototype_courses_%s_%s" % (default_semester.id, student.id), cached_courses)        
                   
    TimerDebugPanel.timer_stop('data_prepare')

    TimerDebugPanel.timer_start('json_prepare_1', 'Przygotowywanie JSON - st1')
    
    cached_all_groups = mcache.get("schedule_prototype_all_groups_%s" % default_semester.id, 'DoesNotExist')   
    if cached_all_groups == 'DoesNotExist':        
        mcache.delete("schedule_prototype_courses_json_%s" % student.id)        
        cached_all_groups = Group.get_groups_by_semester(default_semester)
        mcache.set("schedule_prototype_all_groups_%s" % default_semester.id, cached_all_groups)                
        
    TimerDebugPanel.timer_stop('json_prepare_1')
    TimerDebugPanel.timer_start('json_prepare_2', 'Przygotowywanie JSON - st2')
    all_groups_json = prepare_groups_json(default_semester, cached_all_groups, \
        student=student)
    TimerDebugPanel.timer_stop('json_prepare_2')

    cached_courses_json = mcache.get("schedule_prototype_courses_json_%s" % student.id, 'DoesNotExist')
    if cached_courses_json == 'DoesNotExist':
        cached_courses_json = prepare_courses_json(cached_all_groups, student)
        mcache.set("schedule_prototype_courses_json_%s" % student.id, cached_courses_json)
        
    data = {
        'courses_json': cached_courses_json,
        'groups_json': all_groups_json,
        'courses' : cached_courses,
        'semester' : default_semester,
        'types_list' : Type.get_all_for_jsfilter(),
        'priority_limit': settings.QUEUE_PRIORITY_LIMIT
    }
    return render_to_response('enrollment/records/schedule_prototype.html',\
        data, context_instance = RequestContext(request))
