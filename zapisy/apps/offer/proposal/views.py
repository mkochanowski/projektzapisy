# -*- coding: utf-8 -*-

"""
    Proposal views
"""
from django.contrib                 import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.http                    import Http404
from django.shortcuts               import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http   import require_POST
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription
from apps.enrollment.courses.models.course_type import Type

from apps.offer.proposal.forms import ProposalForm, ProposalDescriptionForm
from apps.offer.proposal.exceptions      import  NotOwnerException


import logging
from apps.offer.proposal.utils import proposal_for_offer, employee_proposal
from apps.users.decorators import employee_required, offer_manager_required
from apps.users.models import Employee

logger = logging.getLogger("")


def main(request):
    return TemplateResponse(request, 'offer/main.html', {} )

def offer(request, slug=None):
    """
    if slug is None, this view shows offer main page,
    else show proposal page
    """
    proposal   = proposal_for_offer(slug)
    proposals  = CourseEntity.get_proposals()
    types_list = Type.get_all_for_jsfilter()
    teachers   = Employee.get_actives()

    return TemplateResponse(request, 'offer/offer.html', locals())




@login_required
@employee_required
def proposal(request, slug=None):
    """
      List of user proposal
    """
    try:
        proposals = CourseEntity.get_employee_proposals(request.user)
        for_review = filter((lambda course: course.get_status() == 5), proposals)
        not_accepted = filter((lambda course: course.get_status() == 0), proposals)
        in_offer = filter((lambda course: 1 <= course.get_status() <= 3), proposals)
        removed = filter((lambda course: course.get_status() == 4), proposals)
        proposal  = employee_proposal(request.user, slug)
    except NotOwnerException:
        return redirect('offer-page', slug=slug)
    except Http404:
        raise Http404

    if proposal:
        return TemplateResponse(request, 'offer/proposal/proposal.html', locals())
    else:
        return TemplateResponse(request, 'offer/proposal/employee_proposals.html', locals())

@login_required
@employee_required
def proposal_edit(request, slug=None):
    proposal = None

    if slug:
        try:
            proposal = CourseEntity.get_employee_proposal(request.user, slug)
            description = CourseDescription.objects.filter(entity=proposal).order_by('-id')[0]
        except NotOwnerException:
            raise Http404
        except ObjectDoesNotExist:
            raise Http404
    else:
        description = None

    proposal_form      = ProposalForm(data=request.POST or None,
                                    instance=proposal, prefix='entity')
    description_form = ProposalDescriptionForm(data=request.POST or None,
                                               instance=description, prefix='description')

    if proposal_form.is_valid() and description_form.is_valid():
        proposal = proposal_form.save(commit=False)
        description = description_form.save(commit=False)
        if not proposal.owner:
            proposal.owner = request.user.employee
        if proposal.status == 5:
            proposal.status = 0
        proposal.save()

        description.author = request.user.employee
        description.entity_id = proposal.id

        if proposal.is_proposal():
            description.save()
        else:
            description.save_as_copy()

        description_form.save_m2m()
        proposal_form.save_m2m()

        messages.success(request, u'Propozycja zapisana')

        return redirect('my-proposal-show', slug=proposal.slug)

    return TemplateResponse(request, 'offer/proposal/form.html', {
        "form": proposal_form,
        "desc": description_form,
        "proposal": proposal
        })

@offer_manager_required
def manage(request):
    proposals = CourseEntity.noremoved.filter(status=0).all()
    return TemplateResponse(request, 'offer/proposal/manage.html', locals())

@offer_manager_required
def proposal_accept(request, slug=None):
    proposal = proposal_for_offer(slug)
    proposal.mark_as_accepted()
    proposal.save()
    messages.success(request, u'Zaakceptowano przedmiot '+proposal.name)
    return redirect('manage')

@offer_manager_required
def proposal_for_review(request, slug=None):
    proposal = proposal_for_offer(slug)
    proposal.mark_for_review()
    proposal.save()
    print proposal.status
    return redirect('manage')
