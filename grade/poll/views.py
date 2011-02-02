# -*- coding: utf-8 -*-
from django.contrib                    import auth
from django.contrib.auth.decorators    import login_required
from django.core.exceptions            import ObjectDoesNotExist
from django.http                       import HttpResponse, \
                                              HttpResponseRedirect
from django.shortcuts                  import render_to_response
from django.template                   import RequestContext
from django.utils                      import simplejson
from fereol.users.decorators           import student_required, employee_required
from django.contrib.auth.decorators    import login_required

from fereol.enrollment.subjects.models import Semester, Group, Subject, GROUP_TYPE_CHOICES
                                              
from fereol.grade.ticket_create.utils  import from_plaintext
from fereol.grade.ticket_create.models import PublicKey, \
                                              PrivateKey
from fereol.grade.poll.models          import Poll, Section, SectionOrdering, \
                                              OpenQuestion, SingleChoiceQuestion, \
                                              OpenQuestionOrdering, Option, \
                                              SingleChoiceQuestionOrdering, \
                                              MultipleChoiceQuestion, \
                                              MultipleChoiceQuestionOrdering, \
                                              SavedTicket, \
                                              SingleChoiceQuestionAnswer, \
                                              MultipleChoiceQuestionAnswer, \
                                              OpenQuestionAnswer, Option
from fereol.users.models               import Type
from fereol.grade.poll.forms           import TicketsForm, \
                                              PollForm, \
                                              FilterMenu
from fereol.grade.poll.utils           import check_signature, \
                                              prepare_data, \
                                              group_polls_and_tickets_by_subject, \
                                              create_slug, \
                                              get_next, \
                                              get_prev, \
                                              get_ticket_and_signed_ticket_from_session, \
                                              check_enable_grade

from fereol.users.models                 import Employee

def default(request):
    grade = Semester.get_current_semester().is_grade_active
    return render_to_response ('grade/base.html', {'grade' : grade }, context_instance = RequestContext ( request ))

@employee_required
def enable_grade( request ):
    if check_enable_grade():
        semester = Semester.get_current_semester()
        semester.is_grade_active = True
        semester.save()   
        grade = True
        return render_to_response ('grade/base.html', {'grade' : grade, 'success' : "Ocena zajęć otwarta" }, context_instance = RequestContext ( request ))
    else:
        return render_to_response ('grade/base.html', {'grade' : False, 'error' : "Oceny nie można otworzyć: brak wygenerowanych kluczy lub ankiet" }, context_instance = RequestContext ( request ))

@employee_required
def disable_grade( request ):
    semester = Semester.get_current_semester()
    semester.is_grade_active = False
    semester.save()
    grade = False
    
    PublicKey.objects.all().delete()
    PrivateKey.objects.all().delete()
    
    # TODO: Coś robić z odpowiedziami
    #       Unieaktywnić ankiety!!!
    
    return render_to_response ('grade/base.html', {'grade' : grade, 'message' : "Zamknięto ocenę zajęć" }, context_instance = RequestContext ( request ))

#### Poll creation ####

@employee_required
def autocomplete(request):
    results = []
    if request.method == "GET":
        if request.GET.has_key(u'term'):
            value = request.GET[u'term']
            # Ignore queries shorter than length 3
            #if len(value) > 2:
            model_results = Option.objects.filter(content__icontains=value)
            results = [ x.content for x in model_results ]
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/javascript')


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

def edit_section(request, section_id):
    from django.template import loader
    form = PollForm()
    form.setFields( None, None, section_id )
    return render_to_response( 'grade/poll/section_edit.html', {"form": form}, context_instance = RequestContext( request ))



@employee_required
def poll_create(request):
    grade = Semester.get_current_semester().is_grade_active
    semester     = None
    group        = None
    type         = None
    studies_type = None
    subject      = None
    # TODO: przeniesc do modeli - porozmawiaz z grupa
    def getGroups(semester, group = None, type = None, subject = None):
        if subject == -1:
            return {}
        if group:
            return group
        if type:
            if subject:
                groups = Group.objects.filter(type=type, subject=subject)
            else:
                groups = Group.objects.filter(type=type)
        else:
            if subject:
                groups = Group.objects.filter(subject=subject)
            else:
                groups = Group.objects.filter(subject__semester = semester)
                
        
        return groups

    message = ""
    polls   = []
    if request.method == "POST":
        semester = int(request.POST.get('semester', 0))
        group    = int(request.POST.get('group', 0))
        type     = int(request.POST.get('type', 0))
        studies_type = int(request.POST.get('studies-type', -1))
        subject  = int(request.POST.get('subject', 0))
        
        groups_without = request.POST.get('poll-only-without', None)
        
        request.session['studies_type'] = studies_type
        request.session['semester']     = semester
        request.session['group']        = group
        request.session['type']         = type
        request.session['subject']      = subject
        request.session['poll_without'] = (groups_without == 'on')
        
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
        elif subject == 0:
            subject    = None
        else:
            subject = -1

        if studies_type > -1:
            studies_type = Type.objects.get(pk=studies_type)
        else:
            studies_type = None

        groups = getGroups(semester, group, type, subject)
        for group in groups:
            if groups_without == 'on' and Poll.get_all_polls_for_group(group):
                continue
            poll = Poll()
            poll.author       = request.user.employee
            poll.title        = request.POST.get('title', '')
            poll.description  = request.POST.get('description', '')
            poll.semester     = semester
            poll.group        = group
            poll.studies_type = studies_type
            poll.save()
            polls.append(unicode(poll))

            i = 1
            for section in request.POST.getlist('sections[]'):
                pollSection = SectionOrdering()
                pollSection.poll = poll
                pollSection.position = i
                pollSection.section = Section.objects.get(pk = section)
                pollSection.save()
                i = i + 1

        if not groups:
            poll = Poll()
            poll.author       = request.user.employee
            poll.title        = request.POST.get('title', '')
            poll.description  = request.POST.get('description', '')
            poll.semester     = semester
            poll.studies_type = studies_type
            poll.save()
            polls.append(unicode(poll))

            i = 1
            for section in request.POST.getlist('sections[]'):
                pollSection = SectionOrdering()
                pollSection.poll = poll
                pollSection.position = i
                pollSection.section = Section.objects.get(pk = section)
                pollSection.save()
                i = i + 1

        message = "Utworzono ankiety!"
        request.session['message'] = message
        request.session['polls_len']   = len(polls)
        request.session['polls']       = polls

        #TODO: check 'is OK?'
        return HttpResponseRedirect('/grade/poll/poll_create')        
    data = {}
    if semester:   
        sem       = Subject.objects.filter(semester = semester).order_by('name')
    else:
        semester_id = Semester.get_current_semester()
        sem         = Subject.objects.filter(semester = semester_id).order_by('name')

    message_sesion = request.session.get('message', None)
    polls     = request.session.get('polls', None)
    polls_len = request.session.get('polls_len', None)
    
    if message_sesion:
        message   = message_sesion
        polls     = request.session['polls']
        polls_len = request.session['polls_len']
        del request.session['message']
        del request.session['polls']
        del request.session['polls_len']

    data['studies_types'] = Type.objects.all()
    data['semesters']    = Semester.objects.all()
    data['subjects']     = sem
    data['message']      = message
    data['polls_len']    = polls_len
    data['polls']        = polls
    data['sections']     = Section.objects.all()
    data['types']        = GROUP_TYPE_CHOICES
    data['group']        = request.session.get('group', None)
    data['type']         = unicode(request.session.get('type', None))
    data['studies_type'] = request.session.get('studies_type', None)
    data['subject_id']   = request.session.get('subject', None)
    data['semester']     = request.session.get('semester', None)
    data['poll_without'] = request.session.get('poll_without', None)
    data['grade'] =  grade
    return render_to_response( 'grade/poll/poll_create.html', data, context_instance = RequestContext( request ))

#
# Poll managment
#

@employee_required
def sections_list( request ):
    data = {}
    data['sections'] = Section.objects.all().order_by('pk')
    data['grade']  = Semester.get_current_semester().is_grade_active
    return render_to_response( 'grade/poll/managment/sections_list.html', data, context_instance = RequestContext( request ))

@employee_required
def show_section( request, section_id):
    form = PollForm()
    form.setFields( None, None, section_id )
    data = {}
    data['form']  = form
    data['grade']  = Semester.get_current_semester().is_grade_active
    return render_to_response( 'grade/poll/managment/show_section.html', data, context_instance = RequestContext( request ))

@employee_required
def get_section(request, section_id):
    form = PollForm()
    form.setFields( None, None, section_id )
    return render_to_response( 'grade/poll/poll_section.html', {"form": form}, context_instance = RequestContext( request ))

@employee_required
def polls_list( request ):
    pass

@employee_required
def groups_without_poll( request ):
    data = {}
    data['groups'] = Poll.get_groups_without_poll()
    data['grade']  = Semester.get_current_semester().is_grade_active
    return render_to_response( 'grade/poll/managment/groups_without_polls.html', data, context_instance = RequestContext( request ))

@employee_required
def poll_manage(request):
    grade = Semester.get_current_semester().is_grade_active
    data = {}
    data['semesters']  = Semester.objects.all() 
    return render_to_response ('grade/poll/manage.html', {'grade' : grade}, context_instance = RequestContext( request ))

@login_required
def declaration( request ):
    # TODO:
    #       Wyświetlanie wyników oceny
    grade = Semester.get_current_semester().is_grade_active
    return render_to_response ('grade/poll/show.html', {'grade' : grade}, context_instance = RequestContext( request ))

@employee_required    
def questionset_create(request):
    grade = Semester.get_current_semester().is_grade_active
    def parse_form(post):
        def choicebox_is_on(value):
            if value == 'on':
                return True
            return False

        section = Section()
        section.title       = post.get("poll[title]")
        section.description = post.get("poll[description]")
        section.save()
        
        questions = post.getlist('poll[question][order][]')

        position = 1
        for question_id in questions:
            question_name        = "poll[question][" + str(question_id) +"]"
            type                 = post.get(question_name + "[type]")

            if type == 'open':
                question = OpenQuestion()

            elif type == 'single' or type == 'leading':
                question = SingleChoiceQuestion()
                question.is_scale = choicebox_is_on(post.get(question_name + "[isScale]"))

            elif type == 'multi':
                question = MultipleChoiceQuestion()
                question.choice_limit = choicebox_is_on(post.get(question_name + "[choiceLimit]"))
                question.has_other    = choicebox_is_on(post.get(question_name + "[hasOther]"))

            else:
                raise WrongType(type)

            question.content     = post.get(question_name + "[title]")
            question.description =  post.get(question_name + "[description]")
            question.save()

            options = post.getlist(question_name + "[answers][]")
            hideOn  = map( lambda (x):( int(x)), post.getlist(question_name + "[hideOn][]"))
            hidenAnswers = []
            i = 1
            for option_name in options:
                option          = Option()
                option.content  = option_name
                option.save()
                question.options.add(option)
                if i in hideOn:
                    hidenAnswers.append(option)
                i = i + 1

            question.save()
            
            if type == 'open':
                container = OpenQuestionOrdering()
                container.question   = question
                container.sections   = section
                container.position   = position
                container.save()

            elif type == 'single' or type == 'leading':
                container = SingleChoiceQuestionOrdering()
                container.question    = question
                container.sections    = section
                container.position   = position
                container.is_leading  = (type == 'leading')
                container.save()
                for opt in hidenAnswers:
                    container.hide_on.add(opt)
                container.save()

            elif type == 'multi':
                container = MultipleChoiceQuestionOrdering()
                container.question   = question
                container.sections    = section
                container.position   = position
                container.save()

            position   = position + 1
    data = {}
    if request.method == "POST":
        parse_form(request.POST)
        request.session['message'] = 'Sekcja dodana'

        #TODO: check 'is OK?'
        return HttpResponseRedirect('/grade/poll/questionset_create')
    if request.session.get('message', None):
        data['message'] = request.session.get('message', None)
        del request.session['message']
          
    data['grade'] = grade
    return render_to_response ('grade/poll/section_create.html', data, context_instance = RequestContext( request ))

def questionset_assign(request):
    pass
    
#### Poll answering ####
@login_required
def grade_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/grade/poll/tickets_enter')

def tickets_enter(request):
    grade = Semester.get_current_semester().is_grade_active
    data = {}
    
    if request.method == "POST":
        form = TicketsForm( request.POST )
        
        if form.is_valid():
            tickets_plaintext = form.cleaned_data[ 'ticketsfield' ]
            try:
                ids_and_tickets   = from_plaintext( tickets_plaintext )
            except:
                ids_and_tickets   = []
            
            if not ids_and_tickets:
                data[ 'error' ] = "Podano niepoprawne bilety."
                data[ 'form' ]  = form
                data[ 'grade' ] = grade
                return render_to_response( 'grade/poll/tickets_enter.html', data, context_instance = RequestContext( request ))
                
            errors   = []
            polls    = []
            finished = []
            for (id, (ticket, signed_ticket)) in ids_and_tickets:
                try:
                    poll       = Poll.objects.get( pk = id )
                    public_key = PublicKey.objects.get( poll = poll )
                    if check_signature( ticket, signed_ticket, public_key ):
                        try:
                            st = SavedTicket.objects.get( poll   = poll,
                                                          ticket = ticket )
                            if st.finished:
                                finished.append(( poll, ticket, signed_ticket ))
                            else:
                                polls.append(( poll, ticket, signed_ticket ))
                        except:
                            st = SavedTicket( poll = poll, ticket = ticket )
                            st.save()
                            polls.append(( poll, ticket, signed_ticket ))
                    else:
                        errors.append(( id, "Nie udało się zweryfikować podpisu pod biletem." ))
                except:
                    errors.append(( id, "Podana ankieta nie istnieje" ))
                    
            request.session[ "errors" ]            = errors
            request.session[ "polls" ]             = map( lambda (s, l): ((s, create_slug( s )), l), group_polls_and_tickets_by_subject( polls ))
            request.session[ "finished" ]          = map( lambda (s, l): ((s, create_slug( s )), l),group_polls_and_tickets_by_subject( finished ))
            

            return HttpResponseRedirect( '/grade/poll/polls/all' )
    else:
        form = TicketsForm()
        
    data[ 'form' ]  = form
    data[ 'grade' ] = grade
    return render_to_response( 'grade/poll/tickets_enter.html', data, context_instance = RequestContext( request ))


def polls_for_user( request, slug ):
    if not 'polls' in request.session.keys():
        return HttpResponseRedirect( '/grade/poll/tickets_enter' )
    
    data = prepare_data( request, slug )
    data[ 'grade' ] = Semester.get_current_semester().is_grade_active
    
    return render_to_response( 'grade/poll/polls_for_user.html', data, context_instance = RequestContext( request ))
    
def poll_answer( request, slug, pid ):
    poll       = Poll.objects.get( pk = pid )
    public_key = PublicKey.objects.get( poll = poll )

    (ticket, signed_ticket) = get_ticket_and_signed_ticket_from_session( request.session, slug, pid )

    data = prepare_data( request, slug )
    data[ 'link_name' ] = poll.to_url_title()
    data[ 'slug' ]      = slug
    data[ 'title' ]     = poll.title
    data[ 'desc' ]      = poll.description
    data[ 'pid']    = pid
        
    try:
        poll_cands = filter( lambda (x, show, l): show, data[ 'polls' ])[0][2]
    except IndexError:
        poll_cands = []
    
    try:
        finished_cands = filter( lambda (x, show, l): show, data[ 'finished' ])[0][2]
    except:
        finished_cands = []

    data[ 'next' ]      = get_next( poll_cands, finished_cands, int( pid ))
    data[ 'prev' ]      = get_prev( poll_cands, finished_cands, int( pid ))
        
    if ticket and signed_ticket and check_signature( ticket, signed_ticket, public_key ):
        st   = SavedTicket.objects.get( ticket = unicode( ticket ), poll = poll )
    
        if request.method == "POST" and not st.finished:
            form = PollForm( request.POST )
            form.setFields( poll, st )
            
            if form.is_valid():
                for key, value in form.cleaned_data.items():
                    
                    if key == 'finish':
                        if value:
                            finit = request.session.get( 'finished', default = [])
                            polls = request.session.get( 'polls',    default = [])
                            
                            slug_polls = filter( lambda ((x, s), ls): slug == s, polls)
                            slug_finit = filter( lambda ((x, s), ls): slug == s, finit) 
                            
                            name = None
                            
                            for ((n, s), ls) in slug_polls: 
                                pd = filter( lambda x: x == (int(pid), ticket, signed_ticket), ls )
                                if pd:
                                    polls.remove(((n, s), ls ))
                                    for poll_data in pd:
                                        ls.remove( poll_data )
                                    if ls: polls.append(((n, s), ls))
                                    name = n
                                    break 
                                    
                            if slug_finit:
                                for ((n, s), ls) in slug_finit:
                                    if n == name:
                                        finit.remove(((n, s), ls))
                                        ls.append((int(pid), ticket, signed_ticket))
                                        finit.append(((n,s), ls))
                                        break
                            else:
                                finit.append(((name, slug), [(int(pid), ticket, signed_ticket)]))
                            
                            def slug_cmp((n1,slug1), (n2,slug2)):
                                if slug1 == "common": return -1
                                if slug2 == "common": return 1
                                return cmp((n1, slug1), (n2,slug2))
                            
                            polls.sort( lambda (x, lx), (y, ly): slug_cmp( x, y ))
                            finit.sort( lambda (x, lx), (y, ly): slug_cmp( x, y ))
                            
                            request.session[ 'finished' ] = finit
                            request.session[ 'polls' ]    = polls
                            
                            st.finished = True
                            st.save()
                            
                    else:
                        [ poll_data, section_data, question_data ] = key.split( '_' )
                        poll_id       = poll_data.split( '-' )[ 1 ]
                        section_id    = section_data.split( '-' )[ 1 ]
                        question_id   = question_data.split( '-' )[ 1 ]
                        question_type = question_data.split( '-' )[ 2 ]
                        other         = len( question_data.split( '-' )) == 4
                        
                        section = Section.objects.get( pk = section_id )
                        
                        if   ( question_type == 'leading' or \
                               question_type == 'single' ):
                            question = SingleChoiceQuestion.objects.get( 
                                            pk = question_id )
                            try:
                                ans = SingleChoiceQuestionAnswer.objects.get(
                                        section      = section,
                                        question     = question,
                                        saved_ticket = st )
                            except ObjectDoesNotExist:
                                ans = SingleChoiceQuestionAnswer(
                                        section      = section,
                                        question     = question,
                                        saved_ticket = st )
                                ans.save()
                            if value:
                                option = Option.objects.get( pk = value )
                                ans.option = option
                                ans.save()
                            else:
                                ans.delete()
                        elif question_type == 'multi' and other:
                            question = MultipleChoiceQuestion.objects.get( 
                                            pk = question_id )
                            try:
                                ans = MultipleChoiceQuestionAnswer.objects.get(
                                        section      = section,
                                        question     = question,
                                        saved_ticket = st )
                            except ObjectDoesNotExist:
                                ans = MultipleChoiceQuestionAnswer(
                                        section      = section,
                                        question     = question,
                                        saved_ticket = st )
                                ans.save()
                            if value:
                                ans.other = value
                                ans.save()
                            else:
                                ans.delete()
                                
                        elif question_type == 'multi':
                            question = MultipleChoiceQuestion.objects.get( 
                                            pk = question_id )
                            try:
                                ans = MultipleChoiceQuestionAnswer.objects.get(
                                        section      = section,
                                        question     = question,
                                        saved_ticket = st )
                            except ObjectDoesNotExist:
                                ans = MultipleChoiceQuestionAnswer(
                                        section      = section,
                                        question     = question,
                                        saved_ticket = st )
                                ans.save()
                            if value:
                                ids = map( int, value )
                                
                                if -1 in ids:
                                    ids.remove( -1 )
                                else:
                                    ans.other = None
                                
                                options = map( lambda id: Option.objects.get( pk = id ),
                                               ids )
                                ans.options = options
                                ans.save()
                            else:
                                ans.delete()
                        elif question_type == 'open':
                            question = OpenQuestion.objects.get( 
                                            pk = question_id )
                            try:
                                ans = OpenQuestionAnswer.objects.get(
                                        section      = section,
                                        question     = question,
                                        saved_ticket = st )
                            except ObjectDoesNotExist:
                                ans = OpenQuestionAnswer(
                                        section      = section,
                                        question     = question,
                                        saved_ticket = st )
                                ans.save()
                            if value:
                                ans.content = value
                                ans.save()
                            else:
                                ans.delete()
        else:
            form = PollForm()
            form.setFields( poll, st )

        data[ 'form' ]      = form
        
        if request.method == "POST" and (data[ 'form' ].is_valid() or st.finished):
            if request.POST.get( 'Next', default=None ):
                return HttpResponseRedirect( '/grade/poll/poll_answer/' + slug + '/' + str( data['next'][0]))
            if request.POST.get( 'Prev', default=None ):
                return HttpResponseRedirect( '/grade/poll/poll_answer/' + slug + '/' + str( data['prev'][0]))
            if request.POST.get( 'Save', default=None ):
                return HttpResponseRedirect( '/grade/poll/poll_answer/' + slug + '/' + str( pid ))
    else:
        data = { 'errors': [ u"Nie masz uprawnień do wypełnienia ankiety " + poll.to_url_title() ], 
                 'slug' : slug,
                 'link_name' : poll.to_url_title() }
    
    data[ 'grade' ] = Semester.get_current_semester().is_grade_active
    
    return render_to_response( 'grade/poll/poll_answer.html', data, context_instance = RequestContext( request ))
   
def poll_end_grading( request ):
    request.session.clear()
    
    return HttpResponseRedirect( '/grade/' )
#### Poll results ####

@login_required
def poll_results(request):
    grade = Semester.get_current_semester().is_grade_active
    group = Employee.get_all_groups( request.user.id )
    
    form = FilterMenu( request.POST )
    data = { 'form' : form, 'list' : group, 'grade' : grade }
    return render_to_response ('grade/poll/poll_results.html', data, context_instance = RequestContext ( request ))


