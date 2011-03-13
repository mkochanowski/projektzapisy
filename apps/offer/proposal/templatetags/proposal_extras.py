# -*- coding: utf-8 -*-

"""
    Extras for proposal
"""

from django.template import Library, Node, TemplateSyntaxError

register = Library()

from apps.offer.proposal.models import Proposal

class SubjectsInOfferNode(Node):
    """
        Adds a list of subjects to template context
    """
    def __init__(self, varname):
        self.varname = varname
    
    def render(self, context):
        context[self.varname] = Proposal.get_by_tag("offer").order_by('name')
        return ''

@register.tag
def get_subjects_in_offer(parser, token):
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError, "get_subjects_in_offer tag takes exactly two arguments"
    if bits[1] != 'as':
        raise TemplateSyntaxError, "first argument to the get_subjects_in_offer tag must be 'as'"
    return SubjectsInOfferNode(bits[2])
