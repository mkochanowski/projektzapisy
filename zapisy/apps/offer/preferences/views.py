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
    proposals = CourseEntity.get_proposals()

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

    form = PreferenceForm(request.POST, instance=pref)
    if form.is_valid():
        form.save()
        return AjaxSuccessMessage(u'Preferencje zapisane')

    return AjaxFailureMessage('InvalidRequest', u'Coś poszło źle')


@require_POST
@employee_required
def hide(request, status):
    """
    Hides preference for employee.
    """
    return set_hidden(request, status)



@employee_required
def save_all_prefs(request):
    """ Saves all preferences. """
    if request.method == 'POST':

        prefs     = request.user.employee.get_preferences()
        formset   = PreferenceFormset(request.POST, queryset=prefs)

        if formset.is_valid():
            formset.save()
            messages.success(request, u'Preferencje zostały zapisane')
            return redirect('prefs-default-view')

        else:
            proposals = CourseEntity.get_proposals()

            return render_to_response(
                'offer/preferences/base.html',
                locals(),
                context_instance = RequestContext(request))

    return redirect('prefs-default-view')

