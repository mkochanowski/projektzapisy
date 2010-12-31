# -*- coding:utf-8 -*-

"""
    Preferences views
"""
import types

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext, Template
from django.utils import simplejson

from offer.preferences.exceptions import *
from offer.preferences.models import Preference
from offer.preferences.utils import *
from offer.proposal.models import Proposal
from offer.proposal.models.types import Types
from users.decorators import employee_required

from offer.preferences.models import PREFERENCE_CHOICES

from django.core.urlresolvers import reverse

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
    prefs = Preference.objects.get_employees_prefs(employee, hidden, types, query).order_by('proposal__name')
    data = {
		'prefs': prefs,
		'proposalTypes': Types.objects.all(),
	}
    def process_pref(pref):
        """
            Processes preference
        """
        obj = {}
        obj['name']           = pref.proposal.name
        obj['id']             = pref.id
        obj['lecture']        = pref.lecture
        obj['review_lecture'] = pref.review_lecture
        obj['tutorial'] = pref.tutorial
        obj['lab']      = pref.lab
        obj['hidden']   = pref.hidden
        obj['desc']     = pref.proposal.description()
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
        Renders subjects description.

        * when format=json is passed via GET:
          return ProposalDescription data as json
          instead of rendering the template
    """
    format = request.GET.get('format', None)
    description_ = get_object_or_404(Proposal, pk=proposal_id).description()
    if format == 'json':
        data = {}
        data['name'] = description_.proposal.name
        data['type'] = description_.type
        data['description'] = description_.description
        data['requirements'] = description_.requirements
        data['comments'] = description_.comments
        data['books'] = dict(
            [(book.order,book.name) for book
             in description_.proposal.books.all()])
        return HttpResponse(simplejson.dumps(data))
    data = {'description': description_}
    return render_to_response(
        'offer/preferences/description.html',
        data)

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
def init_pref(request, prop_id):
    """
        Initialize preference
    """
    try:
        if request.method == 'POST':
            employee = request.user.employee
            course = Proposal.objects.get(pk=prop_id)
            Preference.objects.init_preference(employee, course)
            types = []
            for type in course.description().types():
                types.append(type.lecture_type.id)
            data = {
                'Success': 'OK',
                'name': course.name,
                'id': course.id,
                'types': types,
                'hideurl': reverse('prefs-hide', args = [ course.id ] ),
                'unhideurl': reverse('prefs-unhide', args = [ course.id ] ),
                'prefchoices': PREFERENCE_CHOICES,
                'showlectures': (course.description().lectures > 0),
                'showrepetitories': (course.description().repetitories > 0),
                'showexercises': (course.description().exercises > 0),
                'showlaboratories': (course.description().laboratories > 0),
            }
        else:
            data = {'Failure': 'Use POST'}
    except Proposal.DoesNotExist:
        logger.error('Preferencje - nie znaleziono propozycji przedmiotu o id = %s.' % str(prop_id) )
        data = {'Failure': 'Proposal does not exist'}
    return HttpResponse(simplejson.dumps(data))
