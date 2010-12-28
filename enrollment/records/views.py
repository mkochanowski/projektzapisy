# -*- coding: utf-8 -*-

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

@login_required
def ajaxPin(request):
    data = {}
    try:
        group_id = int(request.POST["GroupId"])
        record = Record.pin_student_to_group(request.user.id, group_id)
        data['Success'] = {}
        data['Success']['Message'] = "Zostałeś przypiety do grupy."
    except NonStudentException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonStudent"
        data['Exception']['Message'] = "Nie możesz się przypiąć, bo nie jesteś studentem."
    except NonGroupException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonGroup"
        data['Exception']['Message'] = "Nie możesz się przypiąć, bo podana grupa nie istnieje."
    except AlreadyPinnedException:
        data['Exception'] = {}
        data['Exception']['Code'] = "AlreadyNotPinned"
        data['Exception']['Message'] = "Nie możesz się przypiąć, bo już jesteś przypięty."
    return HttpResponse(simplejson.dumps(data))

@login_required
def ajaxUnpin(request):
    data = {}
    try:
        group_id = int(request.POST["GroupId"])
        record = Record.unpin_student_from_group(request.user.id, group_id)
        data['Success'] = {}
        data['Success']['Message'] = "Zostałeś wypienty z grupy."
    except NonStudentException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonStudent"
        data['Exception']['Message'] = "Nie możesz zostać wypięty, bo nie jesteś studentem."
    except NonGroupException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonGroup"
        data['Exception']['Message'] = "Nie możesz zostać wypięty, bo podana grupa nie istnieje."
    except AlreadyUnPinnedException:
        data['Exception'] = {}
        data['Exception']['Code'] = "AlreadyNotUnPinned"
        data['Exception']['Message'] = "Nie możesz zostać wypięty, bo nie jesteś przypięty."
    return HttpResponse(simplejson.dumps(data))

@login_required
def ajaxAssign(request):
    data = {}
    try:
        group_id = int(request.POST["GroupId"])
        record = Record.add_student_to_group(request.user.id, group_id)
        data['Success'] = {}
        data['Success']['Message'] = "Zostałeś zapisany do grupy."
    except NonStudentException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonStudent"
        data['Exception']['Message'] = "Nie możesz się zapisać, bo nie jesteś studentem."
    except NonGroupException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonGroup"
        data['Exception']['Message'] = "Nie możesz się zapisać, bo podana grupa nie istnieje."
    except AssignedInThisTypeGroupException:
        data['Exception'] = {}
        data['Exception']['Code'] = "AssignedInThisTypeGroup"
        data['Exception']['Message'] = "Nie możesz się zapisać bo jesteś już zapisany do innej grupy tego typu."
    except AlreadyAssignedException:
        data['Exception'] = {}
        data['Exception']['Code'] = "AlreadyAssigned"
        data['Exception']['Message'] = "Nie możesz się zapisać, bo już jesteś zapisany."
    except OutOfLimitException:
        data['Exception'] = {}
        data['Exception']['Code'] = "OutOfLimit"
        data['Exception']['Message'] = "Nie możesz się zapisać, bo grupa jest już zapełniona."
    except RecordsNotOpenException:
        data['Exception'] = {}
        data['Exception']['Code'] = "RecordsNotOpen"
        data['Exception']['Message'] = "Nie możesz się zapisać, bo zapisy na ten przedmiot nie sa dla ciebie otwarte."
    return HttpResponse(simplejson.dumps(data))

@login_required
def ajaxResign(request):
    data = {}
    try:
        group_id = int(request.POST["GroupId"])
        record = Record.remove_student_from_group(request.user.id, group_id)
        data['Success'] = {}
        data['Success']['Message'] = "Zostałeś wypisany z grupy."
    except NonStudentException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonStudent"
        data['Exception']['Message'] = "Nie możesz się wypisać, bo nie jesteś studentem."
    except NonGroupException:
        data['Exception'] = {}
        data['Exception']['Code'] = "NonGroup"
        data['Exception']['Message'] = "Nie możesz się wypisać, bo podana grupa nie istnieje."
    except AlreadyNotAssignedException:
        data['Exception'] = {}
        data['Exception']['Code'] = "AlreadyNotAssigned"
        data['Exception']['Message'] = "Nie możesz się wypisać, bo nie jesteś zapisany."
    return HttpResponse(simplejson.dumps(data))

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


@login_required
def assign(request, group_id):
    try:
        record = Record.add_student_to_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś zapisany do grupy.")
        return redirect("subject-page", slug=record.group_slug())
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
        request.user.message_set.create(message="Nie możesz się zapisać, bo zapisy na ten przedmiot nie sa dla ciebie otwarte.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@login_required
def queue_assign(request, group_id):
    try:
        queue = Queue.add_student_to_queue(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś zapisany do kolejki.")
        return redirect("subject-page", slug=record.group_slug())
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
        request.user.message_set.create(message="Nie możesz się zapisać, bo zapisy na ten przedmiot nie sa dla ciebie otwarte.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@login_required
def change(request, old_id, new_id):
    try:
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
        request.user.message_set.create(message="Nie możesz się przenieść, bo zapisy na ten przedmiot nie sa dla ciebie otwarte.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@login_required
def resign(request, group_id):
    try:
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

@login_required
def queue_resign(request, group_id):
    try:
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
        data = {
            'all_students' : all_students,
            'students_in_group' : students_in_group,
            'students_in_queue' : students_in_queue,
            'group' : group,
        }
        return render_to_response('enrollment/records/records_list.html', data, context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
        
@login_required
def own(request):
    try:
        groups = Record.get_student_all_detiled_enrollings(request.user.id)
        data = {
            'groups': groups,
        }
        return render_to_response('enrollment/records/schedule.html', data, context_instance=RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Nie masz planu, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
 
@login_required       
def schedulePrototype(request):
    try:
        student_records = Record.get_student_all_detiled_records(request.user.id)
        #subjects = Subject.visible.select_related().all()
        #for sub in subjects:
        #    sub.lecturers = ''
        #    for teacher in sub.teachers.all():
        #        sub.lecturers =  teacher.user.get_full_name() + ',' + sub.lecturers
        all_terms = Term.objects.select_related().all()
        for term in all_terms:
            term.description = term.group
        
        #group_with_subjects = Group.objects.select_related(depth = 2).all()
        #subjects = set([g.subject for g in group_with_subjects])
        #for subject in subjects:
        #    for group in subject.groups_:
        #        group.terms_ = all_terms.filter(group = group)
        semesters = Semester.objects.filter(visible=True)
        semesters_list = [(sem.pk, sem.get_name()) for sem in semesters]
        types = Type.get_all_types_of_subjects()
        types_list = [(type.pk, type.name) for type in Type.objects.all()] 
  
        data = {
            'student_records': student_records,
            #'subjects': subjects,
            'semesters_list' : semesters_list, 
            'types_list' : types_list,
            'terms' : all_terms
        }
        return render_to_response('enrollment/records/schedule_prototype.html', data, context_instance = RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Nie masz planu, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))   
