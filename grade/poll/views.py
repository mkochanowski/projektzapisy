# -*- coding: utf-8 -*-
from django.http                import HttpResponse
from django.shortcuts           import render_to_response
from django.template            import RequestContext
from fereol.grade.poll.models   import Poll
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
                question.description = post.get(question_name + "[description]")
                question.save()
                options = int(post.get(question_name + "[options]"))
                
                for option_id in range (1, options+1):
                    option          = Option()
                    option.question = question
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

def tickets_enter(request):
    pass
    
def poll_answer(request):
    pass
    
def poll_save(request):
    pass
    
#### Poll results ####

def poll_results(request):
    pass

