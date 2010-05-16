# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.shortcuts               import redirect

from fereol.offer.vote.models     import *
from fereol.offer.proposal.models import *
from fereol.users.decorators      import student_required

@student_required
def voteMain( request ):
    data = { 'isVoteActive' : SystemState.is_vote_active() }
    return render_to_response ('offer/vote/voteMain.html', data, context_instance = RequestContext( request ))

@student_required
def voteView( request ):
    votes = SingleVote.get_votes( request.user )
    summer_votes  = []
    winter_votes  = []
    unknown_votes = []
    sum           = 0
    for vote in votes:
        sum = sum + vote.value
        if   vote.subject.in_summer():
            summer_votes.append(vote)
        elif vote.subject.in_winter():
            winter_votes.append(vote)
        else:
            unknown_votes.append(vote)
            
    data = {  'summer_votes'  : summer_votes,
              'winter_votes'  : winter_votes,
              'unknown_votes' : unknown_votes,
              'vote_sum'      : sum }
    return render_to_response ('offer/vote/voteView.html', data, context_instance = RequestContext( request ))
