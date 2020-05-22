import copy
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.users.decorators import employee_required

from .forms import EditProposalForm
from .models import Proposal, ProposalStatus


def offer(request, slug=None):
    """Shows offer main page (with proposals listed in the sidebar).

    If slug is not None, it will also present the proposal in the main content
    area.
    """
    if slug is not None:
        proposal = get_object_or_404(Proposal, slug=slug)
    else:
        proposal = None

    filter_statuses = [ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE, ProposalStatus.WITHDRAWN]
    qs = Proposal.objects.filter(status__in=filter_statuses).order_by('name')
    proposal_list = []
    for p in qs.prefetch_related('effects', 'tags'):
        proposal_dict = p.__json__()
        proposal_dict.update({
            'status': ProposalStatus(p.status)._name_,
            'semester': p.semester,
            'url': reverse('offer-page', args=(p.slug,)),
        })
        proposal_list.append(proposal_dict)
    filter_data = Proposal.prepare_filter_data(qs)

    return render(request, 'proposal/offer.html', {
        "proposal": proposal,
        "proposals": json.dumps(proposal_list),
        "filters_json": json.dumps(filter_data),
    })


@login_required
def syllabus(request, slug):
    """Prints the syllabus for a proposal."""
    proposal = get_object_or_404(Proposal, slug=slug)

    return render(request, 'proposal/syllabus.html', {
        'proposal': proposal,
    })


@employee_required
def my_proposals(request, slug=None):
    proposals_list = Proposal.objects.filter(owner=request.user.employee)
    proposal = None
    if slug is not None:
        proposal = get_object_or_404(Proposal, slug=slug)
    return render(request, 'proposal/my-proposals.html', {
        'proposals_list': proposals_list,
        'proposal': proposal,
    })


@employee_required
def proposal_edit(request, slug=None):
    proposal = None
    if slug is not None:
        # Editing existing proposal.
        proposal = get_object_or_404(Proposal, slug=slug)

        # Check if the user is allowed to edit this proposal.
        if request.user.employee != proposal.owner and not request.user.is_staff:
            raise PermissionDenied
        form = EditProposalForm(instance=proposal)
    if request.method == "POST":
        # Handling filled-in proposal form.
        form = EditProposalForm(request.POST, instance=proposal, user=request.user)
        if form.is_valid():
            instance = form.save()
            messages.success(request, "Pomyślnie zapisano formularz.")
            # Now display form with the saved proposal.
            return redirect('proposal-edit', slug=instance.slug)

    if slug is None and request.method == "GET":
        # Display an empty form for new proposal.
        form = EditProposalForm()
    return render(request, 'proposal/edit-proposal.html', {
        'form': form,
    })


@employee_required
def proposal_clone(request, slug):
    """Provides a proposal form pre-filled with data from other proposal."""
    proposal = get_object_or_404(Proposal, slug=slug)
    clone = copy.copy(proposal)

    form = EditProposalForm(instance=clone)
    form.helper.form_action = reverse('proposal-form')
    return render(request, 'proposal/edit-proposal.html', {
        'form': form,
    })


@employee_required
def proposal_delete_draft(request, slug):
    """Deletes draft of a proposal if it belongs to the requesting employee."""
    proposal = get_object_or_404(Proposal, slug=slug)
    # We actually allow staff members to do that even though they wouldn't see
    # other's drafts witout a link.
    if not proposal.owner == request.user.employee and not request.user.is_staff:
        raise PermissionDenied
    if not proposal.status == ProposalStatus.DRAFT:
        raise PermissionDenied
    proposal.delete()
    messages.info(request, f"Usunięto propozycję <em>{proposal.name}</em>.")
    return redirect('my-proposals')
