# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.shortcuts               import redirect

from fereol.offer.vote.models     import *
from fereol.offer.proposal.models import *

from fereol.users.decorators      import student_required
from fereol.offer.vote.voteForm   import VoteForm

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

@student_required
def vote( request ):
    subs = Proposal.get_by_tag('vote')
    winter_subs  = []
    summer_subs  = []
    unknown_subs = []
    
    for sub in subs:
        if   sub.in_summer():
            summer_subs.append(sub)
        elif sub.in_winter():
            winter_subs.append(sub)
        else:
            unknown_subs.append(sub)

    data = {
		'proposalTypes': proposal.PROPOSAL_TYPES
	}

    if request.method == "POST":
        form = VoteForm( request.POST, 
                         winter  = winter_subs, 
                         summer  = summer_subs,
                         unknown = unknown_subs,
                         voter   = request.user.student )
        data['form'] = form
        
        if form.is_valid():
            sum = 0
            for name, points in form.vote_points(): 
                sum = sum + int(points)
            
            if sum <= SystemState.get_maxVote():
                votes = SingleVote.get_votes(request.user.student)
                for vote in votes: vote.delete()
                
                for name, points in form.vote_points():
                    if int(points) > 0:
                        subject = Proposal.objects.get(name=name)
                        singleVote = SingleVote()
                        singleVote.student = request.user.student
                        singleVote.subject = subject
                        singleVote.state   = SystemState.get_state()
                        singleVote.value   = int(points)
                        singleVote.save()
            
                data['isVoteActive'] = SystemState.is_vote_active()
                data['message'] = u'Głos został pomyślnie zapisany.'
                return render_to_response('offer/vote/voteForm.html', data, context_instance = RequestContext( request ))
            else:
                data['message'] = u'Przekroczono limit głosowania.\
                                  Limit wynosi ' + str(SystemState.get_maxVote()) +\
                                  u'. Oddano głos o watości: ' + str(sum) + '.'
                return render_to_response('offer/vote/voteForm.html', data, context_instance = RequestContext( request ))
    else:
        data['form'] = VoteForm( winter  = winter_subs,
                         summer  = summer_subs,
                         unknown = unknown_subs,
                         voter   = request.user.student )
            
    return render_to_response('offer/vote/voteForm.html', data, context_instance = RequestContext( request ))
