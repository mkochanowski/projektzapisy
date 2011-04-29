# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.utils import simplejson
from django.views.decorators.http import require_POST
from django.utils.datastructures import MultiValueDictKeyError
from django.db import transaction

from apps.enrollment.subjects.models import *
from apps.users.models import *
from apps.enrollment.records.models import *
from apps.enrollment.records.exceptions import *
from apps.enrollment.subjects.views import prepare_subjects_list_to_render

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
        return AjaxFailureMessage('NotAuthenticated', 'Nie jesteś zalogowany.',\
            message_context)

    try:
        group_id = int(request.POST['group'])
        set_enrolled = request.POST['enroll'] == 'true'
    except MultiValueDictKeyError:
        return AjaxFailureMessage.auto_render('InvalidRequest', \
            'Nieprawidłowe zapytanie.', message_context)

    if request.user.student.block:
        return AjaxFailureMessage.auto_render('ScheduleLocked', \
            'Twój plan jest zablokowany.', message_context);

    logger.info('User %s <id: %s> set himself %s to group with id: %s' % \
        (request.user.username, request.user.id, \
        ('enrolled' if set_enrolled else 'not enrolled'), group_id))

    try:
        if set_enrolled:
            group = Group.objects.get(id=group_id)
            moved = Record.is_student_in_subject_group_type(\
                user_id=request.user.id, slug=group.subject_slug(),\
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

        connected_group_ids = None
        if connected_records:
            connected_group_ids = []
            for record in connected_records:
                connected_group_ids.append(record.group.pk)

        if is_ajax:
            return AjaxSuccessMessage(message, connected_group_ids)
        else:
            request.user.message_set.create(message=message)
            return redirect('subject-page', slug=record.group_slug())
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
            return AjaxSuccessMessage(message)
        else:
            request.user.message_set.create(message=message)
            return redirect('subject-page', slug=Group.objects.\
                get(id=group_id).subject_slug())
    except AlreadyNotAssignedException:
        try:
            Queue.remove_student_from_queue(request.user.id, group_id)
            message = 'Zostałeś wypisany z kolejki wybranej grupy.'
        except AlreadyNotAssignedException:
            message = 'Jesteś już wypisany z tej grupy.'
        if is_ajax:
            return AjaxSuccessMessage(message)
        else:
            request.user.message_set.create(message=message)
            return redirect('subject-page', slug=Group.objects.\
                get(id=group_id).subject_slug())
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
                    message_context)
            else:
                request.user.message_set.create(message=message)
                return redirect('subject-page', slug=Group.objects.\
                    get(id=group_id).subject_slug())
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
            message = 'Nie możesz się wypisać, ponieważ zapisy są już zamknięte.'
        return AjaxFailureMessage.auto_render('RecordsNotOpen', message, \
            message_context)
    except NotCurrentSemesterException:
        transaction.rollback()
        message = 'Nie możesz się wypisać z tej grupy, ponieważ znajduje się ona w semestrze innym niż aktualny.'
        return AjaxFailureMessage.auto_render('RecordsNotOpen', message, \
            message_context)

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
def queue_set_priority(request, group_id, method):
    '''
        Sets new priority for queue of some group
    '''
    is_ajax = (method == '.json')
    message_context = None if is_ajax else request

    try:
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
        if priority > 10 or priority < 1:
            return AjaxFailureMessage.auto_render('FatalError', \
                'Nieprawidłowa wartość priorytetu.', message_context);
        if queue.priority != priority:
            queue.set_priority(priority)
        if is_ajax:
            return AjaxSuccessMessage()
        else:
            return redirect("subject-page", slug=queue.group_slug())
    except Queue.DoesNotExist:
    	transaction.rollback()
        return AjaxFailureMessage.auto_render('NotQueued',\
            'Nie jesteś w kolejce do tej grupy.', message_context)

def records(request, group_id):
    '''
        Group records view - list of all students enrolled and queued to group.
    '''
    try:
        group = Group.objects.get(id=group_id)
        students_in_group = Record.get_students_in_group(group_id)
        students_in_queue = Queue.get_students_in_queue(group_id)
        all_students = Student.objects.all()
        data = prepare_subjects_list_to_render(request)
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
    try:
        logger.info('User %s <id: %s> looked at his schedule' %\
            (request.user.username, request.user.id))
        return render_to_response('enrollment/records/schedule.html', {
            'groups': Record.get_student_records(request.user.student)
        }, context_instance=RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message='Nie jesteś studentem.')
        return render_to_response('common/error.html',\
            context_instance=RequestContext(request))
 
@login_required       
def schedule_prototype(request):
    ''' schedule prototype view '''
    try:
        default_semester = Semester.get_default_semester()
        if not default_semester:
            raise RuntimeError('TODO: trzeba to jakoś obsługiwać')

        student_records = Record.get_student_records_ids(request.user,\
            default_semester)
        StudentOptions.preload_cache(request.user.student, default_semester)

        terms_in_semester = Term.get_all_in_semester(default_semester)
        subjects_in_semester = []
        subjects_in_semester_tmp = {}
        for term in terms_in_semester:
            subject = term.group.subject
            if not subject.pk in subjects_in_semester_tmp:
                subject_collection = {
                    'subject': {
                        'id' : subject.pk,
                        'name': subject.name,
                        'short': subject.entity.get_short_name(),
                        'type': subject.type.pk,
                        'is_recording_open': subject.\
                            is_recording_open_for_student(request.user.student),
                        #TODO: kod w prepare_subjects_list_to_render moim
                        #      zdaniem nie zadziała
                        'was_enrolled': 'False',
                    },
                    'terms': []
                }
                subjects_in_semester_tmp.update({
                    subject.pk: subject_collection
                })
                subjects_in_semester.append(subject_collection)
            term_data = {
                'id': term.pk,
                'group': term.group.pk,
                'group_type': int(term.group.type),
                'teacher': term.group.teacher.user.get_full_name(),
                'classroom': int(term.classroom.number),
                'day': int(term.dayOfWeek),
                'start_time': [term.start_time.hour, term.start_time.minute],
                'end_time': [term.end_time.hour, term.end_time.minute],
            }
            subjects_in_semester_tmp[subject.pk]['terms'].\
                append(simplejson.dumps(term_data))
  
        data = {
            'student_records': student_records,
            'subjects' : subjects_in_semester,
            'semester' : default_semester,
            'types_list' : Type.get_all_for_jsfilter()
        }
        return render_to_response('enrollment/records/schedule_prototype.html',\
            data, context_instance = RequestContext(request))
    except Student.DoesNotExist:
        request.user.message_set.create(message='Nie jesteś studentem.')
        return render_to_response('common/error.html', \
            context_instance=RequestContext(request))
