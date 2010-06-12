# -*- coding:utf-8 -*-

"""
    Preferences views
"""

from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, RequestContext, Template
from django.utils import simplejson

from offer.preferences.exceptions import *
from offer.preferences.models import Preference
from offer.preferences.utils import *
from offer.proposal.models import Proposal
from offer.proposal.models.proposal_description import PROPOSAL_TYPES
from users.decorators import employee_required

from offer.preferences.models import PREFERENCE_CHOICES

from django.core.urlresolvers import reverse

@employee_required
def view(request, template):
    """
        Employee preferences' view renderend using the given template.
        Base view for tree_view and list_view. Do not use directly.
        
        Optional GET args:
        * format={json,html}
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
    prefs = Preference.objects.get_employees_prefs(employee, hidden, types, query)
    data = {
		'prefs': prefs,
		'proposalTypes': PROPOSAL_TYPES
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
    if format == 'json':
        return HttpResponse(simplejson.dumps(data))
    if format == 'html':
        return render_to_response_wo_extends(
            template,
            data,
            RequestContext(request))
    unset = get_employees_unset(employee)
    data['unset_offer'] = unset
    return render_to_response(
        template,
        data,
        context_instance = RequestContext(request))

@employee_required
def undecided_list(request):
    """
        Return json with list of unset preferences
    """

    employee = request.user.employee
    unset = get_employees_unset(employee)
    def process_proposal(prop):
        """
            Process proposal
        """
        obj = {}
        obj['id']   = prop.id
        obj['name'] = prop.name
        obj['hideUrl']  = reverse('prefs-hide', args = [ prop.id ] )
        obj['showUrl']  = reverse('prefs-unhide', args = [ prop.id ] )
        obj['url']      = reverse('prefs-init-pref', args = [ prop.id ] )
        obj['type']     = prop.type
        # obj['tags'] ?
        return obj
    unset = map(process_proposal, unset)
    data = {
        'unset': unset
    }
    return HttpResponse(simplejson.dumps(data))

@employee_required
def tree_view(request):
    """
        Preferences as tree
    """
    return view(request, 'offer/preferences/view_tree.html')

@employee_required
def list_view(request):
    """
        Preferences as list
    """
    return view(request, 'offer/preferences/view_list.html')

# TODO: czy ten widok jest wykorzystywany
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
        data = {'Failure': 'Preference does not exist'}
    return HttpResponse(simplejson.dumps(data))

@employee_required
def set_pref(request, pref_id):
    """
    Sets preferences.

    Preferences to change are passed via POST, e.g.
      lecture=2&tutorial=0.
    """
    try:
        if request.method == 'POST':
            pref = Preference.objects.get(pk=pref_id)
            pref.set_preference( lecture=int(request.POST['lecture']), 
                                 tutorial=int(request.POST['tutorial']), 
                                 review_lecture=int(request.POST['review_lecture']), 
                                 lab = int(request.POST['lab']))
            data = {'Success': "OK"}
        else:
            data = {'Failure': 'Use POST'}
    except (Preference.DoesNotExist, UnknownPreferenceValue):
        data = {'Failure': 'Preference does not exist'}
    return HttpResponse(simplejson.dumps(data))

# ? CO TO JEST ? -> 'lecture', 'review_lecture', 'tutorial', 'lab'
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
            data = {
                'Success': 'OK',
                'name': course.name,
                'id': course.id,
                'type': course.description().type,
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
        data = {'Failure': 'Proposal does not exist'}
    return HttpResponse(simplejson.dumps(data))
