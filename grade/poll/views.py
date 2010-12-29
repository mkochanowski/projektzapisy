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
    def parse_form(post):
        poll          = Poll()
        poll.title    = post.get("poll[title]")
        poll.author   = request.user.employee
        poll.save()
        print ("in parse")
        sections = int(post.get("poll[sections]"))
        for section_id in range(1, sections+1):
            print (u"in sections")
            print (section_id) 
            section       = Section()
            section.poll  = poll

            section_name = "poll[section][" + str(section_id) + "]"
            section.title = post.get(section_name + "[title]")
            section.save()

            questions = int( post.get(section_name + "[questions]") )

            for question_id in range(1, questions+1):
                question             = Question()
                question.section     = section
                question.poll        = poll

                question_name        = section_name + "[question][" + str(question_id) +"]"

                question.type        = post.get(question_name + "[type]")
                question.title       = post.get(question_name + "[title]")
                question.description = post.get(question_name + "[description]", 'brak')
                question.save()
                options = int(post.get(question_name + "[options]"))
                print("opsions: " + str(options))
                for option_id in range (1, options+1):
                    option          = Option()
                    option.question = question
                    print ("in:" + str(question_id))
                    option_name     = question_name + "[option][" + str(option_id) + "]"
                    option.title    = post.get(option_name + "[title]")
                    option.save()
                question.save()
            section.save()
        poll.save()


    if request.method == "POST":
          parse_form(request.POST)
          # TODO: przekierowac do listy
    return render_to_response ('grade/poll/poll_create.html', context_instance = RequestContext( request ))


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

