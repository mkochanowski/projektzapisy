# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.utils import simplejson
from django.views.decorators.http import require_POST
from django.utils.datastructures import MultiValueDictKeyError

from apps.enrollment.subjects.models import *
from apps.users.models import *
from apps.enrollment.records.models import *
from apps.enrollment.records.exceptions import *
from apps.enrollment.subjects.views import prepare_subjects_list_to_render

from libs.ajax_messages import *

@require_POST
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
            return AjaxSuccessMessage('Grupa została przypięta do Twojego planu.')
        else:
            Record.unpin_student_from_group(request.user.id, group_id)
            return AjaxSuccessMessage('Grupa została odpięta od Twojego planu.')
    except NonStudentException:
        return AjaxFailureMessage('NonStudent', \
            'Nie możesz przypinać grup do planu, bo nie jesteś studentem.');
    except NonGroupException:
        return AjaxFailureMessage('NonGroup', \
            'Nie możesz przypiąć tej grupy, bo już nie istnieje.');
    except AlreadyPinnedException:
        return AjaxSuccessMessage( \
            'Grupa jest już przypięta do Twojego planu.');
    except AlreadyNotPinnedException:
        return AjaxSuccessMessage( \
            'Grupa jest już odpięta od Twojego planu.');

@require_POST
def set_enrolled(request, method):
    '''
        Set student assigned (or not) to group.
    '''
    if not request.user.is_authenticated():
        return AjaxFailureMessage('NotAuthenticated', 'Nie jesteś zalogowany.')

    is_ajax = (method == '.json')
    message_context = None if is_ajax else request
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
            connected_records = Record.add_student_to_group(request.user.id, group_id)
            record = connected_records[0]
            if len(connected_records) == 1:
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
        return AjaxFailureMessage.auto_render('NonStudent',
            'Nie możesz zapisać lub wypisać się z grupy, ponieważ nie jesteś studentem.', \
            message_context)
    except NonGroupException:
        return AjaxFailureMessage.auto_render('NonGroup',
            'Nie możesz zapisać lub wypisać się z grupy, ponieważ ona już nie istnieje.', \
            message_context)
    #except AssignedInThisTypeGroupException:
    except AlreadyAssignedException:
        message = 'Jesteś już zapisany do tej grupy.'
        if is_ajax:
            return AjaxSuccessMessage(message)
        else:
            request.user.message_set.create(message=message)
            return redirect('subject-page', slug=Group.objects.get(id=group_id).group_slug())
    except AlreadyNotAssignedException:
        message = 'Jesteś już wypisany z tej grupy.'
        if is_ajax:
            return AjaxSuccessMessage(message)
        else:
            request.user.message_set.create(message=message)
            return redirect('subject-page', slug=Group.objects.get(id=group_id).group_slug())
    except OutOfLimitException:
        return AjaxFailureMessage.auto_render('OutOfLimit', # TODO: dopisywanie do kolejki
            'Nie możesz zapisać się do grupy, bo podana jest już pełna.', \
            message_context)
    except RecordsNotOpenException:
        return AjaxFailureMessage.auto_render('RecordsNotOpen',
            'Nie możesz się zapisać, bo zapisy na ten przedmiot nie są dla ' + \
            'Ciebie otwarte.', message_context)

@require_POST
def deleteStudentFromGroup(request, user_id, group_id):
    try:
        
        logged_as_staff = request.user.is_staff

        if(logged_as_staff): 
           user_id_, group_id_ = user_id, group_id
           Records.remove_student_from_group(user_id = user_id_, group_id = group_id_)

           group = Group.objects.get(id=group_id)
           students_in_group = Record.get_students_in_group(group_id)
           all_students = Student.objects.all()
           data = {
              'all_students' : all_students,
              'students_in_group' : students_in_group,
              'group' : group,
           }
        else:
           raise AdminActionException()

    except AdminActionException:
        request.user.message_set.create(message="Nie masz wystarczających praw by wykonać tą akcję.")
        return render_to_response('common/error-window.html', context_instance=RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Podany student nie istnieje.")
        return render_to_response('common/error-window.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Podana grupa nie istnieje.")
        return render_to_response('common/error-window.html', context_instance=RequestContext(request))
    else:    
        return render_to_response('enrollment/records/records_list.html', data, context_instance=RequestContext(request))

@require_POST
@login_required
def blockPlan(request) :
    data = {}
    try:
        logger.info('User %s  <id: %s> uses AJAX to block his/her plan' % (request.user.username, request.user.id))
        if Student.records_block(request.user.id) :
            data['Success'] = {}
            data['Success']['Message'] = "Twój plan został zablokowany"
    except NonStudentException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonStudent"
        data['Exception']['Message'] = "Nie możesz zablokować planu, bo nie jesteś studentem."
    return HttpResponse(simplejson.dumps(data))

@require_POST
@login_required
def unblockPlan(request) :
    data = {}
    try:
        logger.info('User %s  <id: %s> uses AJAX to block his/her plan' % (request.user.username, request.user.id))
        if Student.records_unblock(request.user.id) :
            data['Success'] = {}
            data['Success']['Message'] = "Twój plan został odblokowany"
    except NonStudentException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonStudent"
        data['Exception']['Message'] = "Nie możesz zablokować planu, bo nie jesteś studentem."
    return HttpResponse(simplejson.dumps(data))

@require_POST
@login_required
def assign(request, group_id):
    try:
        if request.user.student.block :
            request.user.message_set.create(message="Twój plan jest zablokowany.")
            return render_to_response('common/error.html', context_instance=RequestContext(request))
        group = Group.objects.get(id=group_id)
        is_student_already_in_subject_group_type = Record.is_student_in_subject_group_type(user_id=request.user.id, slug=group.subject_slug(), group_type=group.type)
        records_list = Record.add_student_to_group(request.user.id, group_id)
        if is_student_already_in_subject_group_type:
        	request.user.message_set.create(message="Zostałeś przeniesiony do grupy.")
        elif len(records_list) == 1:
            request.user.message_set.create(message="Zostałeś zapisany do grupy.")
        else:
            request.user.message_set.create(message="Zostałeś zapisany do wybranej grupy i grupy wykładowej.")
        return redirect("subject-page", slug=records_list[0].group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except AssignedInThisTypeGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać bo jesteś już zapisany do innej grupy tego typu.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except AlreadyAssignedException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo już jesteś zapisany.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except OutOfLimitException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa jest pełna.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except RecordsNotOpenException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo zapisy na ten przedmiot nie są dla ciebie otwarte.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@require_POST
@login_required
def queue_assign(request, group_id):
    try:
        if request.user.student.block :
            request.user.message_set.create(message="Twój plan jest zablokowany.")
            return render_to_response('common/error.html', context_instance=RequestContext(request))
        if Group.objects.get(id=group_id).subject.is_recording_open_for_student(request.user.student):
            queue = Queue.add_student_to_queue(request.user.id, group_id)
            request.user.message_set.create(message="Zostałeś zapisany do kolejki.")
            slug=queue.group_slug()
        else:
            request.user.message_set.create(message="Nie możesz zapisać się do kolejki, bo nie masz otwartych zapisów.")
            slug=Group.objects.get(id=group_id).subject_slug()
        return redirect("subject-page", slug=slug)
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except AlreadyAssignedException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo już jesteś zapisany.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except RecordsNotOpenException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo zapisy na ten przedmiot nie są dla ciebie otwarte.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@require_POST
@login_required
def queue_inc_priority(request, group_id):
    try:
        if request.user.student.block :
            request.user.message_set.create(message="Twój plan jest zablokowany.")
            return render_to_response('common/error.html', context_instance=RequestContext(request))
        group = Group.objects.get(id=group_id)
        queue = Queue.objects.get(student=request.user.student, group=group)
        if queue.priority < 10 :
            queue.set_priority(queue.priority + 1)
        else:
            request.user.message_set.create(message="Nie można zwiększyć priorytetu.")
        return redirect("subject-page", slug=queue.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except AlreadyAssignedException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo już jesteś zapisany.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except RecordsNotOpenException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo zapisy na ten przedmiot nie są dla ciebie otwarte.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@require_POST
@login_required
def queue_dec_priority(request, group_id):
    try:
        if request.user.student.block :
            request.user.message_set.create(message="Twój plan jest zablokowany.")
            return render_to_response('common/error.html', context_instance=RequestContext(request))
        group = Group.objects.get(id=group_id)
        queue = Queue.objects.get(student=request.user.student, group=group)
        if queue.priority > 1 :
            queue.set_priority(queue.priority - 1)
        else:
            request.user.message_set.create(message="Nie można zmniejszyć priorytetu.")
        return redirect("subject-page", slug=queue.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except AlreadyAssignedException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo już jesteś zapisany.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except RecordsNotOpenException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo zapisy na ten przedmiot nie są dla ciebie otwarte.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@require_POST
@login_required
def queue_set_priority(request, group_id, priority):
    try:
        if request.user.student.block :
            request.user.message_set.create(message="Twój plan jest zablokowany.")
            return render_to_response('common/error.html', context_instance=RequestContext(request))
        group = Group.objects.get(id=group_id)
        queue = Queue.objects.get(student=request.user.student, group=group)
        priority = int(priority)
        if priority > 10 or priority < 1:
            request.user.message_set.create(message="Nieprawidłowa wartość priorytetu.")
            return render_to_response('common/error.html', context_instance=RequestContext(request))
        if queue.priority != priority:
            queue.set_priority(priority)
        return HttpResponse(simplejson.dumps({'Success': {'Message': 'OK'}}))
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except AlreadyAssignedException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo już jesteś zapisany.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except RecordsNotOpenException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo zapisy na ten przedmiot nie są dla ciebie otwarte.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@require_POST
@login_required
def change(request, old_id, new_id):
    try:
        if request.user.student.block :
            request.user.message_set.create(message="Twój plan jest zablokowany.")
            return render_to_response('common/error.html', context_instance=RequestContext(request))
        record = Record.change_student_group(request.user.id, old_id, new_id)
        request.user.message_set.create(message="Zostałeś przepisany do innej grupy.")
        return redirect("subject-page", slug=record.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz zmienić grupy, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz zmienić grupy, bo podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except AlreadyNotAssignedException:
        request.user.message_set.create(message="Nie możesz zmienić grupy, bo nie jesteś zapisany.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except OutOfLimitException:
        request.user.message_set.create(message="Nie możesz się przenieść, bo podana grupa jest pełna.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except RecordsNotOpenException:
        request.user.message_set.create(message="Nie możesz się przenieść, bo zapisy na ten przedmiot nie są dla ciebie otwarte.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@require_POST
@login_required
def resign(request, group_id):
    try:
        if request.user.student.block :
            request.user.message_set.create(message="Twój plan jest zablokowany.")
            return render_to_response('common/error.html', context_instance=RequestContext(request))
        record = Record.remove_student_from_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś wypisany z grupy.")
        return redirect("subject-page", slug=record.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except AlreadyNotAssignedException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś zapisany.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@require_POST
@login_required
def queue_resign(request, group_id):
    try:
        if request.user.student.block :
            request.user.message_set.create(message="Twój plan jest zablokowany.")
            return render_to_response('common/error.html', context_instance=RequestContext(request))
        record = Queue.remove_student_from_queue(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś wypisany z kolejki.")
        return redirect("subject-page", slug=record.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

def records(request, group_id):
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
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@login_required
def own(request):
    ''' own schedule view '''
    try:
        groups = Record.get_student_all_detailed_enrollings(request.user.id)
        data = {
            'groups': groups,
        }
        logger.info('User %s <id: %s> looked at his schedule' % (request.user.username, request.user.id))
        return render_to_response('enrollment/records/schedule.html', data, context_instance=RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Nie masz planu, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
 
@login_required       
def schedule_prototype(request):
    ''' schedule prototype view '''
    try:
        default_semester = Semester.get_default_semester()
        if not default_semester:
            raise RuntimeError('TODO: trzeba to jakoś obsługiwać')

        student_records = Record.get_student_records_ids(request.user, default_semester)

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
                        'was_enrolled': 'False', #TODO: kod w prepare_subjects_list_to_render moim zdaniem nie zadziała
                    },
                    'terms': []
                }
                subjects_in_semester_tmp.update({subject.pk: subject_collection})
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
        return render_to_response('enrollment/records/schedule_prototype.html', data, context_instance = RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Nie masz planu, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
