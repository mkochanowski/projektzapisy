# -*- coding:utf-8 -*-

import types
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils import simplejson
from apps.enrollment.courses.models.course import CourseEntity

from apps.offer.preferences.exceptions import *
from apps.offer.preferences.forms import PreferenceFormset, PreferenceForm
from apps.offer.preferences.models import Preference
from apps.offer.preferences.utils import *
from apps.offer.proposal.models import Proposal
from apps.enrollment.courses.models import Type
from apps.users.decorators import employee_required

from apps.offer.preferences.models import PREFERENCE_CHOICES

from django.core.urlresolvers     import reverse
from django.views.decorators.http import require_POST

import logging
from libs.ajax_messages import AjaxSuccessMessage, AjaxFailureMessage

logger = logging.getLogger()

@employee_required
def view(request):

    employee = request.user.employee
    employee.make_preferences()

    prefs     = employee.get_preferences()
    formset   = PreferenceFormset(queryset=prefs)

    return render_to_response(
        'offer/preferences/base.html',
        locals(),
        context_instance = RequestContext(request))


@employee_required
@require_POST
def save(request):

    id = request.POST.get('prefid', None)
    if not id:
        return AjaxFailureMessage('InvalidRequest', u'Niepoprawny identyfikator')

    id = int(id)

    try:
        pref = Preference.objects.get(id=id)
    except ObjectDoesNotExist:
        return AjaxFailureMessage('InvalidRequest', u'Podany obiekt nie istnieje')

    if not pref.employee == request.user.employee:
        return AjaxFailureMessage('InvalidRequest', u'Nie możesz edytować nie swoich preferencji')

    form = PreferenceForm(data=request.POST, instance=pref)
    if form.is_valid:
        available_fields = Preference._meta.get_all_field_names()
        changed_fields = list(set(available_fields) & set(request.POST.keys()))
        a = ''
        for field in changed_fields:
            setattr(pref, field, form[field].value())
        pref.save()
        form = PreferenceForm(instance=pref)
        return render_to_response('offer/preferences/form_row.html', {'form': form, })
    return AjaxFailureMessage('InvalidRequest', u'Coś poszło źle')
