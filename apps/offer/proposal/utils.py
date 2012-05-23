# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from apps.enrollment.courses.models.course import CourseEntity
from apps.offer.proposal.models.proposal import Proposal


def proposal_for_offer(slug):
    if slug:
        try:
            return CourseEntity.get_proposal(slug)
        except ObjectDoesNotExist:
            raise Http404

    return None



def employee_proposal(employee, slug):
    if slug:
        try:
            proposal = CourseEntity.get_employee_proposal(employee, slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        proposal = None

    return proposal