# -*- coding: utf-8 -*-

from django import template

register = template.Library()

from fereol.offer.proposal.models import Proposal

@register.simple_tag
def subjects_in_offer():
    """
    Renders a list of proposals tagged as offer,
    in a form of <li> tagged list.
    """
    proposals = Proposal.get_by_tag("offer")
    text = ''.join( ["<li>" + str(proposal.name) + "</li>"
                     for proposal in proposals] )
    return text
