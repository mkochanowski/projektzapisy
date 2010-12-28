# -*- coding: utf-8 -*-
from django.http                import HttpResponse
from django.shortcuts           import render_to_response
from django.template            import RequestContext

from fereol.users.decorators    import student_required, employee_required

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

def tickets_enter(request):
    pass
    
def poll_answer(request):
    pass
    
def poll_save(request):
    pass
    
#### Poll results ####

def poll_results(request):
    pass

