# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.shortcuts import redirect

from subjects.models import *
from users.models import *
from records.models import *
from exceptions import NonStudentException, NonGroupException, AlreadyAssignedException

from datetime import time



@login_required
def assign(request, group_id):
    try:
        record = Record.add_student_to_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś zapisany do grupy.")
        return redirect("subject-page", slug=record.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo nie jesteś studentem.")
        # trzeba dodac redirecta
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo podana grupa nie istnieje.")
        # trzeba dodac redirecta
    except AlreadyAssignedException:
        request.user.message_set.create(message="Nie możesz się zapisać, bo już jesteś zapisany.")
        # trzeba dodac redirecta

@login_required
def resign(request, group_id):
    try:
        record = Record.remove_student_from_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś wypisany z grupy.")
        return redirect("subject-page", slug=record.group_slug())
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś studentem.")
        # trzeba dodac redirecta
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo podana grupa nie istnieje.")
        # trzeba dodac redirecta
    except AlreadyAssignedException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś zapisany.")
        # trzeba dodac redirecta

@login_required
def own(request):
    try:
        groups = Record.get_student_groups(request.user.id)
        hours = [(hour, "%s:00" % hour) for hour in range(8, 23)]
        days = DAYS_OF_WEEK
        data = {
            'days': days,
            'groups': groups,
            'hours': hours,
        }
        return render_to_response( 'records/own.html', data, context_instance = RequestContext(request))
    except NonStudentException:
        request.user.message_set.create(message="Nie masz planu, bo nie jesteś studentem.")
        # trzeba dodac redirecta
    
    
