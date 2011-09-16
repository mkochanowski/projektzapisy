# -*- coding:utf-8 -*-

"""
    Preferences views
"""
import types

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext, Template
from django.utils import simplejson

from apps.offer.preferences.exceptions import *
from apps.offer.preferences.models import Preference
from apps.offer.preferences.utils import *
from apps.offer.proposal.models import Proposal
from apps.enrollment.courses.models import Type
from apps.users.decorators import employee_required

from apps.offer.preferences.models import PREFERENCE_CHOICES

from django.core.urlresolvers     import reverse
from django.views.decorators.http import require_POST

import logging
logger = logging.getLogger()

@employee_required
def view(request):
    """
        Employee preferences' view.
        
        Optional GET args:
        * hidden={True,False}
        * types=<comma-separated course types list> (ex. =cs_1,seminar)
        * query=<filter>
    """
    format = request.GET.get('format', None)
    hidden = request.GET.get('hidden', True)
    types  = request.GET.get('types',  None)
    query  = request.GET.get('query',  None)
    employee = request.user.employee
    if types:
        types = types.split(',')
    prefs = Preference.objects.get_employees_prefs(employee, hidden, types, query).order_by('proposal__name')\
            .select_related('proposal', 'proposal__description', 'proposal__description__type')
    data = {
        'prefs': prefs,
        'proposalTypes': Type.objects.all().select_related('group'),
    }
    def process_pref(pref):
        """
            Processes preference
        """
        obj = {}
        obj['name']           = pref.proposal.name
        obj['id']             = pref.id
        obj['is_new']         = pref.proposal.is_new()
        obj['lecture']        = pref.lecture
        obj['review_lecture'] = pref.review_lecture
        obj['tutorial'] = pref.tutorial
        obj['lab']      = pref.lab
        obj['hidden']   = pref.hidden
        obj['proposal']     = pref.proposal
        return obj
    data['prefs'] = map(process_pref, data['prefs'])
    unset = get_employees_unset(employee)
    data['unset_offer'] = unset
    return render_to_response(
        'offer/preferences/base.html',
        data,
        context_instance = RequestContext(request))

# TODO: ten widok w tej chwili nie jest wykorzystywany, ale ma/miał być do
#       wyświetlania szczegółów przedmiotu w preferencjach przedmiotów
@employee_required
def description(request, proposal_id):
    """
        Renders courses description.

        * when format=json is passed via GET:
          return ProposalDescription data as json
          instead of rendering the template
    """
    format = request.GET.get('format', None)
    proposal = Proposal.objects.get(id=proposal_id).select_related('description', 'description__type', 'description__type__group').description
    description = proposal.description
    if format == 'json':
        data = {}
        data['name'] = proposal.name
        data['type'] = description.type
        data['description'] = description.description
        data['requirements'] = description.requirements
        data['comments'] = description.comments
        data['books'] = dict(
            [(book.order,book.name) for book
             in description_.proposal.books.all()])
        return HttpResponse(simplejson.dumps(data))
    data = {'description': description_}
    return render_to_response(
        'offer/preferences/description.html',
        data)

@require_POST
@employee_required
def hide(request, pref_id):
    """
    Hides preference for employee.
    """
    try:
        if request.method == 'POST':
            pref = Preference.objects.get(pk=pref_id)
            pref.hide()
            data = {'Success': 'OK'}
        else:
            data = {'Failure': 'Use POST'}
    except Preference.DoesNotExist:
        logger.error('Ukrycie preferencji - nie znaleziono preferencji o id = %s.' % str(pref_id) )
        data = {'Failure': 'Preference does not exist'}
    return HttpResponse(simplejson.dumps(data))

@require_POST
@employee_required
def unhide(request, pref_id):
    """
    Unhides preference.
    """
    try:
        if request.method == 'POST':
            pref = Preference.objects.get(pk=pref_id)
            pref.unhide()
            data = {'Success': 'OK'}
        else:
            data = {'Failure': 'Use POST'}
    except Preference.DoesNotExist:
        logger.error('Pokazanie preferencji - nie znaleziono preferencji o id = %s.' % str(pref_id) )
        data = {'Failure': 'Preference does not exist'}
    return HttpResponse(simplejson.dumps(data))

@employee_required
def save_all_prefs(request):
    """ Saves all preferences. """
    if request.method == 'POST':
        # collect posted data
        posted_data = {}
        for key, value in request.POST.items():
            try:
                key = key.split('-')
                if (len(key) < 2): raise ValueError
                pid = int(key[-1])
                category = '_'.join(key[:-1])
                if not posted_data.has_key(pid):
                    posted_data[pid] = {}
                posted_data[pid][category] = int(value)
            except (ValueError, IndexError,):
                pass
        # save preferences
        for pid, new_pref_values in posted_data.items():
            try:
                pref = Preference.objects.get(pk=pid)
                new_pref_values = dict([(k.encode('utf-8'), v) for k,v in new_pref_values.items()])
                pref.set_preference(**new_pref_values)
            except (Preference.DoesNotExist, UnknownPreferenceValue,):                
                pass
        request.user.message_set.create(message='Zapisano preferencje.')
    return redirect('prefs-default-view')

@employee_required
@require_POST
def init_pref(request, prop_id):
    """
        Initialize preference
    """
    try:
        if request.method == 'POST':
            employee = request.user.employee
            course = Proposal.noremoved.get(pk=prop_id)
            Preference.objects.init_preference(employee, course)
            data = {
                'Success': 'OK',
                'name': course.name,
                'id': course.id,
                'is_new': course.is_new(),
                'type': course.description.type.id,
                'hideurl': reverse('prefs-hide', args = [ course.id ] ),
                'unhideurl': reverse('prefs-unhide', args = [ course.id ] ),
                'prefchoices': PREFERENCE_CHOICES,
                'showlectures': True,
                'showrepetitories': True,
                'showexercises': True,
                'showlaboratories': True,
            }
        else:
            data = {'Failure': 'Use POST'}
    except Proposal.DoesNotExist:
        logger.error('Preferencje - nie znaleziono propozycji przedmiotu o id = %s.' % str(prop_id) )
        data = {'Failure': 'Proposal does not exist'}
    return HttpResponse(simplejson.dumps(data))
