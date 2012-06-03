# -*- coding: utf-8 -*-

"""
    Vote views
"""
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http                    import HttpResponseRedirect, Http404
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.shortcuts               import redirect
from apps.enrollment.courses.models.course import CourseEntity

from apps.offer.vote.models                   import SingleVote, SystemState
from apps.offer.proposal.models               import Proposal
from apps.enrollment.courses.models import Type

from apps.users.decorators      import student_required

@student_required
def vote( request ):
    from vote_form import VoteFormsets

    student = request.user.student
    state   = SystemState.get_state()

    if not state.is_system_active():
        raise Http404

    SingleVote.make_votes(student)

    kwargs = {'student': student, 'state': state}
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



    data = { 'formset':             formset,
             'proposalTypes':       Type.objects.all().select_related('group'),
             'isCorrectionActive' : state.is_correction_active() }

    return render_to_response ('offer/vote/form.html', data, context_instance = RequestContext( request ))

@student_required
def vote_main( request ):
    """
        Vote main page
    """
    sytem_state = SystemState.get_state()
    data = { 'isVoteActive' : sytem_state.is_system_active() }
    return render_to_response ('offer/vote/index.html', data, context_instance = RequestContext( request ))


@student_required
def vote_view( request ):
    """
        View of once given vote
    """
    votes = SingleVote.get_votes( request.user.student )
    summer_votes  = []
    winter_votes  = []
    unknown_votes = []
    vote_sum      = 0
    for vote in votes:
        vote_sum = vote_sum + vote.correction
        if   vote.entity.is_summer():
            summer_votes.append(vote)
        elif vote.entity.is_winter():
            winter_votes.append(vote)
        else:
            unknown_votes.append(vote)
            
    data = {  'summer_votes'  : summer_votes,
              'winter_votes'  : winter_votes,
              'unknown_votes' : unknown_votes,
              'vote_sum'      : vote_sum}
    return render_to_response ('offer/vote/view.html', data, context_instance = RequestContext( request ))


def vote_summary( request ):
    """
        summary for vote
    """
    subs = CourseEntity.get_vote()
    
    summer = []
    winter = []
    unknown = []
    
    for sub in subs:
        points, voters_count, _ = SingleVote.get_points_and_voters( sub )
        
        if sub.is_winter():
            winter.append( (points, voters_count, sub) )
        elif sub.is_summer():
            summer.append( (points, voters_count, sub) )
        else:
            unknown.append( (points, voters_count, sub) )
            
    data = { 'winter'  : winter,
             'summer'  : summer,
             'unknown' : unknown, }
            
    return render_to_response('offer/vote/summary.html', data, context_instance = RequestContext( request ))
    
def proposal_vote_summary( request, slug ):
    """
        Summary for given course
    """
    try:
        course = CourseEntity.noremoved.get( slug=slug )
    except ObjectDoesNotExist:
        raise Http404

    points, votes, voters = SingleVote.get_points_and_voters( course )

    data = { 'proposal' : course,
             'points'   : points,
             'votes'    : votes,
             'voters'    : voters}
           
    return render_to_response('offer/vote/proposal_summary.html', data, context_instance = RequestContext( request ))
