# -*- coding: utf-8 -*-

"""
    Vote views
"""

from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.shortcuts               import redirect

from apps.offer.vote.models                   import SingleVote, SystemState
from apps.offer.proposal.models               import Proposal
from apps.enrollment.courses.models import Type

from apps.users.decorators      import student_required
from apps.offer.vote.vote_form  import VoteForm

@student_required
def vote_main( request ):
    """
        Vote main page
    """
    data = { 'isVoteActive' : SystemState.is_vote_active() }
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

@student_required
def vote( request ):
    """
        Voting
    """
    subs = Proposal.get_by_tag('vote').order_by('name')

    winter_list = Proposal.get_pks_by_tag('winter')
    summer_list = Proposal.get_pks_by_tag('summer')

    winter_subs  = []
    summer_subs  = []
    unknown_subs = []
    
    for sub in subs:
        if  sub.pk in summer_list:
            summer_subs.append(sub)
        elif sub.pk in winter_list:
            winter_subs.append(sub)
        else:
            unknown_subs.append(sub)

    data = {
               'proposalTypes': Type.objects.all(),
       }

    if request.method == "POST":
        form = VoteForm( request.POST, 
                         winter  = winter_subs, 
                         summer  = summer_subs,
                         unknown = unknown_subs,
                         voter   = request.user.student )
        data['form'] = form
        
        if form.is_valid():
            vote_sum = 0
            for name, points in form.vote_points(): 
                vote_sum = vote_sum+ int(points)
            
            if vote_sum <= SystemState.get_max_vote():
                votes = SingleVote.get_votes(request.user.student)
                for vote_ in votes: 
                    vote_.delete()
                
                for name, points in form.vote_points():
                    if int(points) > 0:
                        course = Proposal.objects.get(name=name)
                        single_vote = SingleVote()
                        single_vote.student = request.user.student
                        single_vote.course = course
                        single_vote.state   = SystemState.get_state()
                        single_vote.value   = int(points)
                        single_vote.save()
            
#                data['message'] = u'Głos został pomyślnie zapisany.'
#                return render_to_response('offer/vote/form.html', data, context_instance = RequestContext( request ))
                return vote_view( request )
            else:
                request.user.message_set.create(message=\
                    'Przekroczono limit głosowania. Limit wynosi ' + \
                    str(SystemState.get_max_vote()) + \
                    ', a oddano głos o watości: ' + str(vote_sum) + '.')
                return render_to_response('offer/vote/form.html', data, context_instance = RequestContext( request ))
    else:
        data['form'] = VoteForm( winter  = winter_subs,
                         summer  = summer_subs,
                         unknown = unknown_subs,
                         voter   = request.user.student )
            
    return render_to_response('offer/vote/form.html', data, context_instance = RequestContext( request ))

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
