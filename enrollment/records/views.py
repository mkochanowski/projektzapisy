# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.shortcuts import redirect

from enrollment.subjects.models import *
from users.models import *
from enrollment.records.models import *
from exceptions import NonStudentException, NonGroupException, AlreadyAssignedException, \
    AlreadyNotAssignedException, AlreadyPinnedException, AlreadyNotPinnedException

from datetime import time

@login_required
def ajaxPin(request):
    try:
        group_id = request.POST["GroupId"]
        record = Record.pin_student_to_group(request.user.id, group_id)
        message = "Zostałeś przypięty do grupy."
    except NonStudentException:
        message="Nie możesz się przypiąć, bo nie jesteś studentem."
    except NonGroupException:
        message="Nie możesz się przypiąć, bo podana grupa nie istnieje."
    except AlreadyPinnedException:
        message="Nie możesz się przypiąć, bo już jesteś przypięty."
    return HttpResponse(message)

@login_required
def ajaxUnpin(request):
    try:
        group_id = request.POST["GroupId"]
        record = Record.unpin_student_from_group(request.user.id, group_id)
        message="Zostałeś wypięty z grupy."
    except NonStudentException:
        message="Nie możesz się wypiąć, bo nie jesteś studentem."
    except NonGroupException:
        message="Nie możesz się wypiąć, bo podana grupa nie istnieje."
    except AlreadyNotAssignedException:
        message="Nie możesz się wypiąć, bo nie jesteś zapisany."
    return HttpResponse(message)

@login_required
def assign(request, group_id):
    try:
        record = Record.add_student_to_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś zapisany do grupy.")
        return redirect("subject-page", slug=record.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo nie jesteś studentem.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa nie istnieje.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except AlreadyAssignedException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo już jesteś zapisany.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))

@login_required
def change(request, old_id, new_id):
    try:
        record = Record.change_student_group(request.user.id, old_id, new_id)
        request.user.message_set.create(message="Zostałeś przepisany do innej grupy.")
        return redirect("subject-page", slug=record.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz zmienić grupy, bo nie jesteś studentem.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz zmienić grupy, bo podana grupa nie istnieje.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except AlreadyNotAssignedException:
        request.user.message_set.create(message="Nie możesz zmienić grupy, bo nie jesteś zapisany.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
@login_required
def resign(request, group_id):
    try:
        record = Record.remove_student_from_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś wypisany z grupy.")
        return redirect("subject-page", slug=record.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś studentem.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo podana grupa nie istnieje.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except AlreadyNotAssignedException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś zapisany.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))

def records(request, group_id):
    try:
        students = Record.get_students_in_group(group_id)
        data = {
            'students' : students,
        }
        return render_to_response('enrollment/records/records_list.html', data, context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Podana grupa nie istnieje.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
        
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
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
 
@login_required       
def schedulePrototype(request):
    try:
        student_records = Record.get_student_all_detiled_records(request.user.id)
        subjects = Subject.objects.all()
        for subject in subjects:
            subject.groups_ = Group.objects.filter(subject=subject)
            for group in subject.groups_:
                group.terms_ = group.get_all_terms()
        data = {
            'student_records': student_records,
            'subjects': subjects,
        }
        return render_to_response('enrollment/records/schedule_prototype.html', data, context_instance = RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Nie masz planu, bo nie jesteś studentem.")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
        
    
    
    
    
