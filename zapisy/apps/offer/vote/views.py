from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render

from apps.enrollment.courses.models import Semester
from apps.enrollment.utils import mailto
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.offer.vote.models import SingleVote, SystemState
from apps.users.decorators import student_required

from .forms import prepare_vote_formset


@student_required
def vote(request):
    """Renders voting form to the student and handles voting POST requests."""
    system_state = SystemState.get_current_state()

    if not system_state:
        messages.warning(request, "Głosowanie nie jest w tym momencie aktywne.")
        return redirect('/')

    if not system_state.is_vote_active() and (system_state.correction_active_semester() is None):
        messages.warning(request, "Głosowanie nie jest w tym momencie aktywne.")
        return redirect('vote-main')

    if request.method == 'POST':
        formset = prepare_vote_formset(system_state, request.user.student, post=request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Zapisano głos.")
        else:
            messages.error(request, "\n".join(formset.non_form_errors()))

    else:
        formset = prepare_vote_formset(system_state, request.user.student)

    if system_state.is_vote_active():
        template_name = 'vote/form.html'
    elif system_state.correction_active_semester():
        template_name = 'vote/form_correction.html'
    return render(request, template_name, {'formset': formset})


@login_required
def vote_main(request):
    """Vote main page."""
    system_state = SystemState.get_current_state()

    if system_state is None:
        messages.warning(request, "Głosowanie nie jest w tym momencie aktywne.")
        return redirect('/')

    is_vote_active = system_state.is_vote_active() or system_state.correction_active_semester()

    data = {
        'is_vote_active': is_vote_active,
        'max_points': SystemState.DEFAULT_MAX_POINTS,
        'semester': Semester.get_current_semester()
    }
    return render(request, 'vote/index.html', data)


@student_required
def my_vote(request):
    """Shows the student his own vote."""
    system_state = SystemState.get_current_state()

    if system_state is None:
        messages.warning(request, "Głosowanie nie jest w tym momencie aktywne.")
        return redirect('/')

    votes = SingleVote.objects.meaningful().filter(state=system_state, student=request.user.student)

    is_vote_active = system_state.is_vote_active() or system_state.correction_active_semester()

    return render(request, 'vote/my_vote.html', {
        'votes': votes,
        'is_vote_active': is_vote_active,
    })


@login_required
def vote_summary(request):
    """Summarizes the voting period."""
    state = SystemState.get_current_state()

    if state is None:
        messages.warning(request, "Głosowanie nie jest w tym momencie aktywne.")
        return redirect('/')

    # Sum all the vote true values for proposal. This is the same as
    # `true_val()` in SingleVote manager or SingleVote.val property.
    votes_sum_agg = models.Sum(models.Case(
        models.When(singlevote__correction=0, then='singlevote__value'),
        default='singlevote__correction'
    ), filter=models.Q(singlevote__state=state))
    # Count all the non-zero votes for the proposal.
    votes_count_agg = models.Count(
        'singlevote__id',
        filter=models.Q(singlevote__state=state) &
        ~models.Q(singlevote__value=0, singlevote__correction=0),
        distinct=True)

    proposals = Proposal.objects.filter(status=ProposalStatus.IN_VOTE)
    proposals = proposals.annotate(total=votes_sum_agg).annotate(count=votes_count_agg)

    return render(request, 'vote/summary.html', {
        'proposals': proposals,
    })


@login_required
def proposal_vote_summary(request, slug):
    """Lists students voting for a proposal."""
    proposal: Proposal = get_object_or_404(Proposal, slug=slug)
    state = SystemState.get_current_state()

    if state is None:
        messages.warning(request, "Głosowanie nie jest w tym momencie aktywne.")
        return redirect('/')

    votes = SingleVote.objects.meaningful().filter(state=state, proposal=proposal).select_related(
        'student', 'student__user').true_val()

    total = votes.aggregate(total=models.Sum('true_val')).get('total', 0)

    voters = [vote.student for vote in votes]

    return render(request, 'vote/proposal_summary.html', {
        'proposal': proposal,
        'votes': votes,
        'total': total,
        'mailto_voters': mailto(request.user, voters, bcc=False),
        'mailto_voters_bcc': mailto(request.user, voters, bcc=True)
    })
