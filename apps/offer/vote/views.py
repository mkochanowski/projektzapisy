# -*- coding: utf-8 -*-

"""
    Vote views
"""
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponseRedirect, Http404
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.shortcuts               import redirect

from apps.offer.vote.models                   import SingleVote, SystemState
from apps.offer.proposal.models               import Proposal
from apps.enrollment.courses.models import Type

from apps.users.decorators      import student_required

@student_required
def vote( request ):
    from vote_form import VoteFormsets

    student = request.user.student
    state = SystemState.get_state()

    if not state.is_system_active():
        raise Http404

    kwargs = {}
    kwargs['student'] = student
    kwargs['state']   = state
    if request.method == 'POST':
        kwargs['post'] = request.POST

    formset = VoteFormsets(**kwargs)

    if request.method == 'POST':

        if formset.is_valid():
            formset.save()
            messages.success( request, "Oddano poprawny głos" )

        else:
            messages.error( request, "Nie udało się oddać głosu" )
            for error in formset.errors:
                messages.error(request, error)

    else:
        SingleVote.make_votes(student)

    data = { 'formset': formset, 'proposalTypes': Type.objects.all(), 'isCorrectionActive' : state.is_correction_active() }
    return render_to_response ('offer/vote/form.html', data, context_instance = RequestContext( request ))

@student_required
def vote_main( request ):
    """
        Vote main page
    """
    data = { 'isVoteActive' : SystemState.is_system_active() }
    return render_to_response ('offer/vote/index.html', data, context_instance = RequestContext( request ))


@student_required
def vote_view( request ):
    """
        View of once given vote
    """
    votes = SingleVote.get_votes( request.user.student ).order_by('course__name')
    summer_votes  = []
    winter_votes  = []
    unknown_votes = []
    vote_sum      = 0
    for vote_ in votes:
        vote_sum = vote_sum + vote_.value
        if   vote_.course.in_summer():
            summer_votes.append(vote_)
        elif vote_.course.in_winter():
            winter_votes.append(vote_)
        else:
            unknown_votes.append(vote_)
            
    data = {  'summer_votes'  : summer_votes,
              'winter_votes'  : winter_votes,
              'unknown_votes' : unknown_votes,
              'vote_sum'      : vote_sum}
    return render_to_response ('offer/vote/view.html', data, context_instance = RequestContext( request ))


def vote_summary( request ):
    """
        summary for vote
    """
    subs = Proposal.get_by_tag('vote').order_by('name')
    
    summer = []
    winter = []
    unknown = []
    
    for sub in subs:
        points, voters = SingleVote.get_points_and_voters( sub )
        
        if sub.in_winter():
            winter.append( (points, voters, sub) )
        elif sub.in_summer():
            summer.append( (points, voters, sub) )
        else:
            unknown.append( (points, voters, sub) )
            
    data = { 'winter'  : winter,
             'summer'  : summer,
             'unknown' : unknown, }
            
    return render_to_response('offer/vote/summary.html', data, context_instance = RequestContext( request ))
    
def proposal_vote_summary( request, slug ):
    """
        Summary for given course
    """
    course = Proposal.objects.get( slug=slug )
    points, votes = SingleVote.get_points_and_voters( course )
    voters = SingleVote.get_voters( course )
    
    data = { 'proposal' : course,
             'points'   : points,
             'votes'    : votes,
             'voters'    : voters}
           
    return render_to_response('offer/vote/proposal_summary.html', data, context_instance = RequestContext( request ))
