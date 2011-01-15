# -*- coding: utf-8 -*-
from django.contrib                    import auth
from django.contrib.auth.decorators    import login_required
from django.http                       import HttpResponse, \
                                              HttpResponseRedirect
from django.shortcuts                  import render_to_response
from django.template                   import RequestContext
from django.utils                      import simplejson
from fereol.users.decorators           import student_required, employee_required
from fereol.enrollment.subjects.models import Semester, Group, Subject, GROUP_TYPE_CHOICES
                                              
from fereol.grade.ticket_create.utils  import from_plaintext
from fereol.grade.ticket_create.models import PublicKey, \
                                              PrivateKey
from fereol.grade.poll.models          import Poll, Section, SectionOrdering, \
                                              OpenQuestion, SingleChoiceQuestion, \
                                              OpenQuestionOrdering, Option, \
                                              SingleChoiceQuestionOrdering, \
                                              MultipleChoiceQuestion, \
                                              MultipleChoiceQuestionOrdering
from fereol.users.models               import Type
from fereol.grade.poll.forms           import TicketsForm


def default(request):
	grade = Semester.get_current_semester().is_grade_active
	return render_to_response ('grade/base.html', {'grade' : grade }, context_instance = RequestContext ( request ))

def enable_grade( request ):
    semester = Semester.get_current_semester()
    semester.is_grade_active = True
    semester.save()   
    return render_to_response ('grade/base.html', { 'message' : "Otwarto ocenę zajęć" }, context_instance = RequestContext ( request ))
    
def disable_grade( request ):
    semester = Semester.get_current_semester()
    semester.is_grade_active = False
    semester.save()
    
    PublicKey.objects.all().delete()
    PrivateKey.objects.all().delete()
    
    # TODO: Coś robić z odpowiedziami
    
    return render_to_response ('grade/base.html', { 'message' : "Zamknięto ocenę zajęć" }, context_instance = RequestContext ( request ))


#### Poll creation ####

@employee_required
def ajax_get_groups(request):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            type    = int( request.POST.get('type', '0') )
            subject = int( request.POST.get('subject', '0') )
            groups  = groups_list( Group.objects.filter(type=type, subject=subject).order_by('teacher'))
            message = simplejson.dumps( groups )
    return HttpResponse(message)

def groups_list( groups ):
    group_list = []
    for group in groups:
        group_list.append( (group.pk, unicode(group.teacher)) )
    return group_list

@employee_required
def ajax_get_subjects(request):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            semester = int( request.POST.get('semester', '0') )
            subjects = subjects_list( Subject.objects.filter(semester=semester).order_by('name') )
            message = simplejson.dumps( subjects )
    return HttpResponse(message)

def subjects_list( subjects ):
    subject_list = []
    for subject in subjects:
        subject_list.append( (subject.pk , unicode(subject.name)) )
    return subject_list 

@employee_required
def poll_create(request):

    # TODO: przeniesc do modeli - porozmawiaz z grupa
    def getGroups(semester, group = None, type = None, subject = None):
        if group:
            return group
        if type:
            if subject:
                print type
                groups = Group.objects.filter(type=type, subject=subject)
            else:
                print type
                groups = Group.objects.filter(type=type)
        else:
            if subject:
                groups = Group.objects.filter(subject=subject)
            else:
                roups = Group.objects.filter(subject__semester = semester)
        return groups

    message = ""
    if request.method == "POST":
        semester = int(request.POST.get('semester', 0))
        group    = int(request.POST.get('group', 0))
        type     = str(request.POST.get('type', 0))
        studies_type = int(request.POST.get('studies-type', -1))
        subject  = int(request.POST.get('subject', 0))
 
        if semester > 0:
            semester = Semester.objects.get(pk = semester)
        else:
            semester = Semester.get_current_semester()

        if group > 0:
            group    = Group.objects.get(pk = group)
        else:
            group    = None

        if type == 0:
            type = None

        if subject > 0:
            subject = Subject.objects.get(pk = subject)
        else:
            subject = None

        if studies_type > -1:
            studies_type = Type.objects.get(pk=studies_type)
        else:
            studies_type = None

        groups = getGroups(semester, group, type, subject)
        print groups
        for group in groups:
            poll = Poll()
            poll.author       = request.user.employee
            poll.title        = request.POST.get('title', '')
            poll.description  = request.POST.get('description', '')
            poll.semester     = semester
            poll.group        = group
            poll.studies_type = studies_type
            poll.save()

            i = 1
            for section in request.POST.getlist('sections[]'):
                pollSection = SectionOrdering()
                pollSection.poll = poll
                pollSection.position = i
                pollSection.section = Section.objects.get(pk = section)
                pollSection.save()
                i = i + 1

        message = "Utworzono ankietę!"
    data = {}
    data['studies_type'] = Type.objects.all()
    data['semesters']  = Semester.objects.all()    
    last_semester      = Semester.objects.all().order_by('-pk')[0]
    data['subjects']   = Subject.objects.filter(semester = last_semester).order_by('name')
    data['message']    = message
    data['sections']   = Section.objects.all()
    data['types']   = GROUP_TYPE_CHOICES
    return render_to_response( 'grade/poll/poll_create.html', data, context_instance = RequestContext( request ))

def poll_manage(request):
    pass

def declaration( request ):
    # TODO:
    #       Wyświetlanie wyników oceny
    return render_to_response ('grade/poll/show.html', context_instance = RequestContext( request ))

@employee_required    
def questionset_create(request):
    def parse_form(post):
        def choicebox_is_on(value):
            if value == 'on':
                return True
            return False

        section = Section()
        section.title       = post.get("poll[title]")
        section.descritpion = post.get("poll[description]")
        section.save()

        questions = post.getlist('poll[question][order][]')

        position = 1
        for question_id in questions:
            question_name        = "poll[question][" + str(question_id) +"]"
            type                 = post.get(question_name + "[type]")

            if type == 'open':
                question = OpenQuestion()

            elif type == 'single':
                question = SingleChoiceQuestion()
                question.is_scale = choicebox_is_on(post.get(question_name + "[isScale]"))

            elif type == 'multi':
                question = MultipleChoiceQuestion()
                question.choice_limit = choicebox_is_on(post.get(question_name + "[choiceLimit]"))
                question.has_other    = choicebox_is_on(post.get(question_name + "[hasOther]"))

            else:
                raise WrongType(type)

            question.content = post.get(question_name + "[title]")
            question.save()

            options = post.getlist(question_name + "[answers][]")
            for option_name in options:
                option          = Option()
                option.content  = option_name
                option.save()
                question.options.add(option)

            question.save()
            
            if type == 'open':
                container = OpenQuestionOrdering()
                container.question   = question
                container.sections   = section
                container.save()

            elif type == 'single':
                container = SingleChoiceQuestionOrdering()
                container.question   = question
                container.sections    = section
                container.is_leading = choicebox_is_on(post.get(question_name + "[isLeading]"))
                container.save()

            elif type == 'multi':
                container = MultipleChoiceQuestionOrdering()
                container.question   = question
                container.sections    = section
                container.save()

    data = {}
    if request.method == "POST":
        parse_form(request.POST)
        data['message']  = 'Sekcja dodana'

    return render_to_response ('grade/poll/section_create.html', data, context_instance = RequestContext( request ))


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

