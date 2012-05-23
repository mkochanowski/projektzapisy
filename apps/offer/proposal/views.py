# -*- coding: utf-8 -*-

"""
    Proposal views
"""
from django.contrib                 import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http                    import Http404
from django.shortcuts               import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http   import require_POST
from apps.enrollment.courses.models.course import CourseEntity

from apps.offer.proposal.forms import ProposalForm
from apps.offer.proposal.exceptions      import  NotOwnerException


import logging
from apps.offer.proposal.utils import proposal_for_offer, employee_proposal

logger = logging.getLogger("")


def main(request):
    return TemplateResponse(request, 'offer/main.html', {} )

def offer(request, slug=None):
    """
    if slug is None, this view shows offer main page,
    else show proposal page
    """
    proposal  = proposal_for_offer(slug)
    proposals = CourseEntity.get_proposals()

    return TemplateResponse(request, 'offer/offer.html', locals())




@login_required
def proposal(request, slug=None):
    """
      List of user proposal
    """
    try:
        proposals = CourseEntity.get_employee_proposals(request.user.employee)
        proposal  = employee_proposal(request.user.employee, slug)
    except NotOwnerException:
        return redirect('offer-page', slug=slug)

    return TemplateResponse(request, 'offer/proposal/proposal.html', locals())


@login_required
def proposal_edit(request, slug=None):

    proposal = None
    proposals = CourseEntity.get_employee_proposals(request.user.employee)

    if slug:
        try:
            proposal = CourseEntity.get_employee_proposal(request.user.employee, slug)
        except NotOwnerException:
            raise Http404

    if request.method == 'POST':
        form = ProposalForm(data=request.POST, instance=proposal)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.owner = request.user.employee
            messages.success(request, u'Propozycja zapisana')
    else:
        form = ProposalForm(instance=proposal)

    return TemplateResponse(request, 'offer/proposal/form.html', locals())
