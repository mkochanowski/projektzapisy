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


@login_required
def subjectTerms(request,subject_id):
	"""Wyświetla stronę zapisów na wybrany przedmiot"""
	student = request.user.student
	semester = Semester.objects.filter(visible = True)
	subject = Subject.objects.get(id = subject_id)
	groups = Group.objects.filter(subject = subject).select_related().order_by('type')
	records = Record.objects.filter(student = student).select_related()
	groups_enr = [record.group for record in records]
	groups_enr = filter(lambda x: x.subject.id == subject.id,groups_enr)
#	groups_signed = map(lambda x: x in groups_enr,groups)
	groups_final = map(lambda x: (x,x in groups_enr),groups)
	enrolled_by_type ={}
	for g,z in groups_final:
		if g.type in enrolled_by_type.keys():
			enrolled_by_type[g.type] = enrolled_by_type[g.type] or z
		else:
			enrolled_by_type[g.type] = z
	show_unsigned = True in enrolled_by_type.values()				
	return render_to_response("mobile/subject_terms.html",{'e': enrolled_by_type,'subject': subject,'groups' : records,'g2': groups_final,'su': show_unsigned},context_instance = RequestContext(request))

@login_required
def assign(request,group_id):
    try:
        record = Record.add_student_to_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś zapisany do grupy.")
	group = Group.objects.get(id=group_id)
	subject = group.subject.id
        return redirect("subject-terms", subject_id=subject)
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
def resign(request, group_id):

    try:
        record = Record.remove_student_from_group(request.user.id, group_id)
        request.user.message_set.create(message="Zostałeś wypisany z grupy.")
	group = Group.objects.get(id=group_id)
	subject = group.subject.id
        return redirect("subject-terms", subject_id=subject)
    except NonStudentException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonGroupException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo podana grupa nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except AlreadyNotAssignedException:
        request.user.message_set.create(message="Nie możesz się wypisać, bo nie jesteś zapisany.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

