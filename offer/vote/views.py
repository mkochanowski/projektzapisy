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
    return render_to_response ('offer/vote/voteMain.html', context_instance = RequestContext( request ))

@student_required
def voteForm ( requst ):
    subjects = Proposal.objects.all()
    # zamienic na: 
    # subjects = Proposal.get_by_tag('vote')
    # jak już będzie można dodawać tagi
    
    summer = []
    winter = []
    undef  = []
    voted  = []
    
    # DODAĆ WYCIĄGANIE ZAPISANYCH DANYCH!!!
    
    for sub in subjects:
        if sub.in_summer():
            summer.append((sub, None))
        elif sub.in_winter():
            winter.append((sub, None))
        else:
            undef.append((sub, None))
    
    maxLen = max(len(summer), len(winter), len(undef))
    for i in range(len(summer), maxLen): summer.append(None)
    for i in range(len(winter), maxLen): winter.append(None)
    for i in range(len(undef),  maxLen): undef. append(None)
    
    data = { 'subjects'  : zip(winter, summer, undef),
             'maxPoints' : range(0, MAX_VOTE+1) }
          
    return render_to_response ('offer/vote/voteForm.html', data, context_instance = RequestContext( request ))
