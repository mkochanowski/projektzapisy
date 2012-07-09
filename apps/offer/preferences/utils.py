# -*- coding: utf-8 -*-

"""
    Preferences utilities
"""
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse
from django.template import loader
from django.template.loader_tags import ExtendsNode
from apps.offer.preferences.models import Preference
from apps.offer.proposal.models import Proposal
from libs.ajax_messages import AjaxFailureMessage, AjaxSuccessMessage

def render_to_response_wo_extends(template_name, data, context):
    """
    A simple template renderer that removes template's
    base ExtendsNode, if present.
    """
    context.update(data)
    template = loader.get_template(template_name)
    base_node = template.nodelist[0]
    if type(base_node) == ExtendsNode:
        template.nodelist = base_node.nodelist
    return HttpResponse(template.render(context))

def get_employees_unset(employee):
    """
    Returns courses in offer for which employee's preferences
    are undetermined.
    """
    return Proposal.get_offer()\
                    .exclude(preference__employee=employee)

    
def set_hidden(request, status):
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

    pref.hidden = status
    pref.save()

    return AjaxSuccessMessage(u'Preferencje zapisane')