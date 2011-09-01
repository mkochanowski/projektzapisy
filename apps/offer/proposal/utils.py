# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from apps.offer.proposal.models.proposal import Proposal


def prepare_proposals_data(request):
    data = {}


    """
        Proposals list
    """
    try:
        if not request.user.is_staff:
            _ = request.user.employee
        proposals = Proposal.noremoved.order_by('name')
    except ObjectDoesNotExist:
        proposals = Proposal.filtred.order_by('name')

    data['proposals'] = proposals

    return data