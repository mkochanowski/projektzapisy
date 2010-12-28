# -*- coding: utf-8 -*-
from django.http                import HttpResponse, \
                                       HttpResponseRedirect
from django.shortcuts           import render_to_response
from django.template            import RequestContext

from fereol.users.decorators    import student_required, employee_required
from fereol.grade.poll.forms    import TicketsForm

from fereol.grade.ticket_create.utils import from_plaintext

from django.contrib import auth
from django.contrib.auth.decorators import login_required

def default(request):
    return render_to_response ('grade/base.html', context_instance = RequestContext ( request ))

def enable_grade( request ):
    ############################################################################
    ##      TODO:                                                             ##
    ##              USTAWIĆ STATUS OCENY NA AKTYWNY                           ##
    ############################################################################    
    return render_to_response ('grade/base.html', { 'message' : "Otwarto ocenę zajęć" }, context_instance = RequestContext ( request ))
    
def disable_grade( request ):
    ############################################################################
    ##      TODO:                                                             ##
    ##              USTWIĆ STATUS OCENY NA NIEAKTYWNY                         ##
    ##              usunąć wygenerowane klucze                                ##
    ##              zrobić coś z wynikami oceny                               ##
    ############################################################################
    return render_to_response ('grade/base.html', { 'message' : "Zamknięto ocenę zajęć" }, context_instance = RequestContext ( request ))


#### Poll creation ####

def poll_create(request):
    pass
    
def questionset_create(request):
    pass

def questionset_assign(request):
    pass
    
#### Poll answering ####
@login_required
def grade_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/grade/poll/tickets_enter')

def tickets_enter(request):
    data = {}
    
    if request.method == "POST":
        form = TicketsForm( request.POST )
        
        if form.is_valid():
            tickets_plaintext = form.cleaned_data[ 'ticketsfield' ]
            tickets = from_plaintext( tickets_plaintext )
            print tickets
            ## TERAZ TRZEBA Z TYMI PODPISANYMI BILETAMI PRZEJŚĆ DALEJ
    else:
        form = TicketsForm()
    
    data[ 'form' ] = form
    return render_to_response( 'grade/poll/tickets_enter.html', data, context_instance = RequestContext( request ))
    
def poll_answer(request):
    pass
    
def poll_save(request):
    pass
    
#### Poll results ####

def poll_results(request):
    pass

