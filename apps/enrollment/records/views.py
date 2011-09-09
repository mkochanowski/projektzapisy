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

from apps.enrollment.courses.models import *
from apps.users.models import *
from apps.enrollment.records.models import *
from apps.enrollment.records.exceptions import *
from apps.enrollment.courses.views import prepare_courses_list_to_render

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
        queued = Queue.queued.filter(group__course=course)
        enrolled_ids = Record.enrolled.filter(group__course=course, \
            student=student).values_list('group__id', flat=True)
        queued_ids = queued.filter(student=student). \
            values_list('group__id', flat=True)
        pinned_ids = Record.pinned.filter(group__course=course, \
            student=student).values_list('group__id', flat=True)
        queue_priorities = Queue.queue_priorities_map(queued)
        student_counts = Group.get_students_counts(groups)

        data = {}
        for group in groups:
            data[group.id] = group.serialize_for_ajax(
                enrolled_ids, queued_ids, pinned_ids,
                queue_priorities, student_counts, student)
        return data

    try:
        group = Group.objects.get(id=group_id)
        if set_enrolled:
            moved = Record.is_student_in_course_group_type(\
                user_id=request.user.id, slug=group.course_slug(),\
                group_type=group.type) #TODO: omg ale crap
            connected_records = Record.add_student_to_group(request.user.id,\
                group_id)
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
            record = Record.remove_student_from_group(request.user.id, group_id)
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
        group = Group.objects.get(id=group_id)
        queue = Queue.objects.get(student=request.user.student, group=group)
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

def prepare_courses_with_terms(terms, records = []):
    courses_list = []
    courses_map = {}
    def add_course_to_map(course):
        if course.pk in courses_map:
            return
        course_info = {
            'object': course,
            'info': {
                'id' : course.pk,
                'name': course.name,
                'short': course.entity.get_short_name(),
                'type': course.type and course.type.pk or 1,
                'slug': course.slug,
            },
            'terms': []
        }
        courses_map[course.pk] = course_info
        courses_list.append(course_info)
    for term in terms:
        course = term.group.course
        add_course_to_map(course)
        term_info = {
            'id': term.pk,
            'group': term.group.pk,
            'classroom': term.classroom.number and int(term.classroom.number) or 0,
            'day': int(term.dayOfWeek),
            'start_time': [term.start_time.hour, term.start_time.minute],
            'end_time': [term.end_time.hour, term.end_time.minute],
        }
        courses_map[course.pk]['terms'].append({
            'id': term.pk,
            'object': term,
            'info': term_info
        })
    for record in records:
        add_course_to_map(record.group.course)
        
    courses_list = sorted(courses_list, \
        key=lambda course: course['info']['name'])
    return courses_list

def prepare_groups_json(student, semester, groups):
    record_ids = Record.get_student_records_ids(student, semester)
    queue_priorities = Queue.queue_priorities_map(
        Queue.get_student_queues(student, semester))
    student_counts = Group.get_students_counts(groups)
    groups_json = []
    for group in groups:
        groups_json.append(group.serialize_for_ajax(
            record_ids['enrolled'], record_ids['queued'], record_ids['pinned'],
            queue_priorities, student_counts, student
        ))
    return '[' + (', '.join(groups_json)) + ']'

def prepare_courses_json(groups, student):
    courses_json = []
    for group in groups:
        courses_json.append(group.course.serialize_for_ajax(student))
    return '[' + (', '.join(courses_json)) + ']'

@login_required
def own(request):
    ''' own schedule view '''

    default_semester = Semester.get_default_semester()
        
    try:
        student = request.user.student
        courses = prepare_courses_with_terms(\
            Term.get_all_in_semester(default_semester, student),\
            Record.get_student_enrolled_objects(student, default_semester))  
        is_student = True
    except Student.DoesNotExist:
        try:
            employee = request.user.employee
            is_student = False
            student = None
            courses = prepare_courses_with_terms(\
                Term.get_all_in_semester(default_semester, employee=employee))
        except Employee.DoesNotExist:
            request.user.message_set.create(message='Nie jesteś pracownikiem ani studentem.')
            return render_to_response('common/error.html', \
                context_instance=RequestContext(request))


    if not default_semester:
        data = {
            'terms_by_days': {},
            'courses': [],
            'points': [],
            'points_type': None,
            'points_sum': 0
        }
        request.user.message_set.create(message='Brak aktywnego semestru.')
        return render_to_response('enrollment/records/schedule.html',\
            data, context_instance = RequestContext(request))

    terms_by_days = [None for i in range(8)] # dni numerowane od 1
    for course in courses:
        for term in course['terms']:
            day = int(term['object'].dayOfWeek)
            if not terms_by_days[day]:
                terms_by_days[day] = {
                    'day_id': day,
                    'day_name': term['object'].get_dayOfWeek_display(),
                    'terms': []
                }
            terms_by_days[day]['terms'].append(term)
            term.update({ # TODO: do szablonu
                'json': simplejson.dumps(term['info'])
            })
    terms_by_days = filter(lambda term: term, terms_by_days)

    # TODO: tylko grupy, na które jest zapisany
    all_groups = Group.get_groups_by_semester(default_semester)
    all_groups_json = prepare_groups_json(student, default_semester, all_groups)

    if is_student:
        points_type = student.program.type_of_points
        course_objects = map(lambda course: course['object'], courses)
        points = Course.get_points_for_courses(course_objects, student.program)
        points_sum = reduce(lambda sum, k: sum + points[k].value, points, 0)  
        points_type = student.program.type_of_points 
    else:
        points_type = None
        points = None
        points_sum = None 
        points_type = None  
    data = {
        'courses_json': prepare_courses_json(all_groups, student),
        'groups_json': all_groups_json,
        'terms_by_days': terms_by_days,
        'courses': courses,
        'points': points,
        'points_type': points_type,
        'points_sum': points_sum,
        'priority_limit': settings.QUEUE_PRIORITY_LIMIT
    }

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

    StudentOptions.preload_cache(student, default_semester)

    enrolled_students_counts = Group.numbers_of_students(default_semester, True)
    queued_students_counts = Group.numbers_of_students(default_semester, False)
    courses = prepare_courses_with_terms(\
        Term.get_all_in_semester(default_semester))
    for course in courses:
        course['info'].update({
            'is_recording_open': course['object'].\
                is_recording_open_for_student(student),
            #TODO: kod w prepare_courses_list_to_render moim zdaniem nie
            #      zadziała
            'was_enrolled': 'False',
        })
        for term in course['terms']:
            term['info'].update({
                'enrolled_count': int(enrolled_students_counts[term['id']]) \
                    if enrolled_students_counts.has_key(term['id']) else 0,
                'queued_count': int(queued_students_counts[term['id']]) \
                    if queued_students_counts.has_key(term['id']) else 0,
            })
            term.update({ # TODO: do szablonu
                'json': simplejson.dumps(term['info'])
            })

    all_groups = Group.get_groups_by_semester(default_semester)
    all_groups_json = prepare_groups_json(student, default_semester, all_groups)
    
    data = {
        'courses_json': prepare_courses_json(all_groups, student),
        'groups_json': all_groups_json,
        'courses' : courses,
        'semester' : default_semester,
        'types_list' : Type.get_all_for_jsfilter(),
        'priority_limit': settings.QUEUE_PRIORITY_LIMIT
    }
    return render_to_response('enrollment/records/schedule_prototype.html',\
        data, context_instance = RequestContext(request))
