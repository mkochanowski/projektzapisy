# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription

def proposal_for_offer(slug):
    if slug:
        try:
            return CourseEntity.get_proposal(slug)
        except ObjectDoesNotExist:
            raise Http404

    return None


def employee_proposal(user, slug):
    if slug:
        try:
            proposal = CourseEntity.get_employee_proposal(user, slug)
            proposal.information = CourseDescription.objects.filter(entity=proposal).order_by('-id')[0]
        except (ObjectDoesNotExist, IndexError) as e:
            raise Http404
    else:
        proposal = None

    return proposal