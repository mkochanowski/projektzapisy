# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import loader
from django.template.loader_tags import ExtendsNode
from offer.proposal.models import Proposal

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
    props = Proposal.get_by_tag('offer')
    props = props.exclude(preference__employee=employee)
    return props
    
