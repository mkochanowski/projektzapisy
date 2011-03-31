# -*- coding: utf-8 -*-
from django.contrib                    import auth, messages

from django.contrib.auth.decorators    import login_required
from django.core.exceptions            import ObjectDoesNotExist, \
                                              ValidationError
from django.core.urlresolvers          import reverse
from django.http                       import HttpResponse, \
                                              HttpResponseRedirect,\
                                              Http404
from django.shortcuts                  import render_to_response
from django.template                   import RequestContext
from django.utils                      import simplejson
from apps.users.decorators             import student_required, employee_required
from django.contrib.auth.decorators    import login_required

from apps.enrollment.subjects.models import Semester, Group, Subject, GROUP_TYPE_CHOICES
                                              
from apps.grade.ticket_create.utils  import from_plaintext
from apps.grade.ticket_create.models import PublicKey, \
                                              PrivateKey
from apps.grade.poll.models          import Poll, Section, SectionOrdering, \
                                              OpenQuestion, SingleChoiceQuestion, \
                                              OpenQuestionOrdering, Option, \
                                              SingleChoiceQuestionOrdering, \
                                              MultipleChoiceQuestion, \
                                              MultipleChoiceQuestionOrdering, \
                                              SavedTicket, \
                                              SingleChoiceQuestionAnswer, \
                                              MultipleChoiceQuestionAnswer, \
                                              OpenQuestionAnswer, Option, Template, \
                                              TemplateSections
from apps.users.models               import Type
from apps.grade.poll.forms           import TicketsForm, \
                                              PollForm, \
                                              FilterMenu
from apps.grade.poll.utils           import check_signature, \
                                              prepare_data, \
                                              group_polls_and_tickets_by_subject, \
                                              create_slug, \
                                              get_next, \
                                              get_prev, \
                                              get_ticket_and_signed_ticket_from_session,\
                                              group_polls_by_subject, \
                                              group_polls_by_teacher, \
                                              getGroups,\
                                              declination_poll,\
                                              declination_section

from apps.users.models               import Employee
from django.core.paginator             import Paginator, InvalidPage, EmptyPage

from form_utils                        import get_section_form_data, \
                                              validate_section_form, \
                                              section_save
from django.utils.safestring           import SafeUnicode, mark_safe
from apps.news.models                import News


@employee_required
def templates( request ):
    """
        Preparation of template list;
    """
    data = {}
    templates = Template.objects.filter(deleted=False)
    paginator = Paginator(templates, 25)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        templates = paginator.page(page)
    except (EmptyPage, InvalidPage):
        templates = paginator.page(paginator.num_pages)

    data['templates'] = templates
    data['grade']  = Semester.get_current_semester().is_grade_active
    return render_to_response( 'grade/poll/managment/templates.html', data, context_instance = RequestContext( request ))

@employee_required
def use_templates( request ):
    pass

@employee_required
def template_actions( request ):
    data = {}
    data['grade']  = Semester.get_current_semester().is_grade_active

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_selected':
            data['templates'] = get_objects( request, Template)
            return render_to_response( 'grade/poll/managment/templates_confirm.html',
                                       data, context_instance = RequestContext( request ))

        elif action == 'use_selected':
            pass

    return HttpResponseRedirect(reverse('grade-poll-templates'))

def get_objects( request, object ):
    pks = request.POST.getlist('_selected_action')
    return object.objects.filter( pk__in=pks)

@employee_required
def delete_templates( request ):
    if request.method == 'POST':
        counter = delete_objects(request, Template, 'templates[]')
        message = u'Usunięto ' + unicode(counter) + u' ' + declination_section(counter)
        messages.info(request, SafeUnicode(message))
            
    return HttpResponseRedirect(reverse('grade-poll-templates'))

def delete_objects( request, object, object_list ):
    pks = request.POST.getlist(object_list)
    counter = 0
    for pk in pks:
        element = object.objects.get(pk=pk)
        element.deleted = True
        element.save()
        counter = counter + 1

    return counter

@employee_required
def show_template( request, template_id ):
    pass

# save poll as template
# @author mjablonski
@employee_required
def create_template(request):
    if request.method <> "POST":
        raise Http404

    type         = int(request.POST.get('type', 0))
    studies_type = int(request.POST.get('studies-type', -1))
    subject      = int(request.POST.get('subject', 0))

    if studies_type > -1:
        studies_type = Type.objects.get(pk=studies_type)
    else:
        studies_type = None

    if subject > 0:
        subject = Subject.objects.get(pk=subject)
    elif subject == 0:
        subject = None
    else:
        subject = -1

    if type == 0:
        type = None

    tmpl = Template()
    tmpl.title        = request.POST.get('title', '')
    tmpl.description  = request.POST.get('description', '')
    tmpl.studies_type = studies_type
    if subject == -1:
        tmpl.no_subject = True
        tmpl.subject    = None
    else:
        tmpl.no_subject = False
        tmpl.subject    = subject

    tmpl.group_type   = type

    tmpl.save()
    for section in request.POST.getlist('sections[]'):
        sections = TemplateSections()
        sections.template = tmpl
        sections.section  = Section.objects.get(pk=section)
        sections.save()

    return HttpResponseRedirect( reverse('grade-poll-templates') )


def rules(request):
    grade = Semester.get_current_semester().is_grade_active
    return render_to_response ('grade/rules.html', {'grade' : grade }, context_instance = RequestContext ( request ))

@employee_required
def enable_grade( request ):
    semester = Semester.get_current_semester()
    
    if semester.is_grade_active:
        messages.error( request, "Nie można otworzyć oceny; ocena jest już otwarta")
    elif Poll.get_polls_for_semester().count() == 0:
        messages.error( request, "Nie można otworzyć oceny; brak ankiet")
    elif Poll.get_current_semester_polls_without_keys().count() != 0:
        messages.error( request, "Nie można otworzyć oceny; brak kluczy dla ankiet")
    else:
        semester.is_grade_active = True
        news = News()
        news.author   = request.user
        news.title    = u"Otwarto ocenę zajęć"
        news.body     = u"Ocena zajęć została otwarta. Zapraszamy do wypełniania ankiet."
        news.category = 'grade'
        news.save()
        semester.save()
         
        messages.success(request, "Ocena zajęć otwarta" )
    
    return HttpResponseRedirect('/news/grade')

@employee_required
def disable_grade( request ):
    semester = Semester.get_current_semester()
    
    if semester.is_grade_active:
        news = News()
        news.author   = request.user
        news.title    = u"Zamknięto ocenę zajęć"
        news.body     = u"Ocena zajęć zakończyła się. Można już oglądać wyniki ankiet."
        news.category = 'grade'
        news.save()
    
        semester.is_grade_active = False
        semester.save()
        
        PublicKey.objects.all().delete()
        PrivateKey.objects.all().delete()
        
        for st in SavedTicket.objects.all():
            # TODO: oznaczyć je jako archiwalne!
            st.finished = True
            st.save()
        
        messages.success( request, "Zamknięto ocenę zajęć" )
    else:
        messages.error( request, "Nie można zamknąć oceny; system nie był uruchomiony" )
    
    return HttpResponseRedirect('/news/grade')

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
def poll_create(request, group_id = 0):
    grade = Semester.get_current_semester().is_grade_active
    if grade:
        messages.error( request, "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona" )
        return HttpResponseRedirect('/news/grade')
    semester     = None
    group        = None
    type         = None
    studies_type = None
    subject      = None
    

    message = ""
    polls   = []

    if request.method == "POST":
        semester     = int(request.POST.get('semester', 0))
        group        = int(request.POST.get('group', 0))
        type         = int(request.POST.get('type', 0))
        studies_type = int(request.POST.get('studies-type', -1))
        subject      = int(request.POST.get('subject', 0))
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
            group    = Group.objects.filter(pk = group)
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
    
        if (request.POST.get('title', '') == ''):
            messages.error(request, "Nie można utworzyć ankiety; brak tytułu")
            return HttpResponseRedirect('/news/grade')

        if (request.POST.getlist('sections[]') == []):
            messages.error(request, "Nie można utworzyć ankiety; ankieta jest pusta")
            return HttpResponseRedirect('/news/grade')
        groups = getGroups(semester, group, type, subject)
        for group in groups:
            if groups_without == 'on' and Poll.get_all_polls_for_group(group):
                continue
            if not request.user.employee.has_privileges_for_group(group.pk):
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

        message  = "Utworzono ankiety!"
        message += ("<br>Liczba utworzonych ankiet: %d" % (len( polls )))
        message += "<ul>"
        for poll in polls:
            message += ("<li>%s</li>" % poll )
        message += "</ul>"
        message  = SafeUnicode( message )
        request.session['message'] = message
        request.session['polls_len']   = len(polls)
        request.session['polls']       = polls

        #TODO: check 'is OK?'
        return HttpResponseRedirect(reverse('grade-poll-poll-create'))        
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
        polls     = request.session.get('polls')
        polls_len = request.session.get('polls_len')
        request.session['message']   = None
        request.session['polls']     = None
        request.session['polls_len'] = None

    data['studies_types'] = Type.objects.all()
    data['semesters']    = Semester.objects.all()
    data['subjects']     = sem
    #- data['message']      = message
    messages.info( request, message )
    data['polls_len']    = polls_len
    data['polls']        = polls
    data['sections']     = Section.objects.filter(deleted=False)
    data['types']        = GROUP_TYPE_CHOICES

    if group_id > 0:
        group = Group.objects.get(pk=group_id)
        data['group']        = int(group_id)
        data['type']         = group.type
        data['subject_id']   = group.subject.pk
        data['semester']     = group.subject.semester.pk
        data['groups']       = Group.objects.filter(type=group.type, subject=group.subject).order_by('teacher')
        
    else:
        data['group']        = request.session.get('group', None)
        data['type']         = unicode(request.session.get('type', None))
        data['subject_id']   = request.session.get('subject', None)
        data['semester']     = request.session.get('semester', None)
        
    data['studies_type'] = request.session.get('studies_type', None)
    data['poll_without'] = request.session.get('poll_without', None)
    data['grade'] =  grade
    
    return render_to_response( 'grade/poll/poll_create.html', data, context_instance = RequestContext( request ))

#
# Poll managment
#
    
@employee_required
def sections_list( request ):
    """
        Preparation of sections list; if user is member of the staff he will also
        be able to edit and delete sections; employees without special privileges
        aren't allowed to any such action.
    """
    data = {}
    sections   = Section.objects.filter(deleted=False)
    paginator = Paginator(sections, 25)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        sections = paginator.page(page)
    except (EmptyPage, InvalidPage):
        sections = paginator.page(paginator.num_pages)
    
    
    data['sections'] = sections
    data['grade']  = Semester.get_current_semester().is_grade_active
    return render_to_response( 'grade/poll/managment/sections_list.html', data, context_instance = RequestContext( request ))

@employee_required
def show_section( request, section_id):
    form = PollForm()
    form.setFields( None, None, section_id )
    data = {}
    data['form']    = form
    data['grade']   = Semester.get_current_semester().is_grade_active
    data['message'] = request.session.get('message', None)
    data['section'] = Section.objects.get(pk=section_id)
    try:
        del request.session['message'] 
    except:
        pass
    return render_to_response( 'grade/poll/managment/show_section.html', data, context_instance = RequestContext( request ))

@employee_required
def get_section(request, section_id):
    form = PollForm()
    form.setFields( None, None, section_id )
    return render_to_response( 'grade/poll/poll_section.html', {"form": form}, context_instance = RequestContext( request ))

@employee_required
def delete_section( request ):
    counter = 0
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_selected':
            pks = request.POST.getlist('_selected_action')
            for pk in pks:
                section = Section.objects.get(pk=pk)
                section.deleted = True
                section.save()
                counter = counter + 1

    message = u'Usunięto ' + unicode(counter) + u' ' + declination_section(counter)
    messages.info(request, SafeUnicode(message))
    return HttpResponseRedirect(reverse('grade-poll-sections-list'))

@employee_required
def polls_list( request ):
    data = {}
    polls     = Poll.objects.filter(deleted=False)
    paginator = Paginator(polls, 25)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        polls = paginator.page(page)
    except (EmptyPage, InvalidPage):
        polls = paginator.page(paginator.num_pages)
    
    
    data['polls']  = polls
    data['grade']  = Semester.get_current_semester().is_grade_active
    return render_to_response( 'grade/poll/managment/polls_list.html', data, context_instance = RequestContext( request ))

@employee_required
def show_poll( request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    form = PollForm()
    form.setFields( poll, None, None )
    data = {}
    data['form']    = form
    data['grade']   = Semester.get_current_semester().is_grade_active
    data['message'] = request.session.get('message', None)
    return render_to_response( 'grade/poll/managment/show_poll.html', data, context_instance = RequestContext( request ))

@employee_required
def delete_poll( request ):
    counter = 0
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_selected':
            pks = request.POST.getlist('_selected_action')
            for pk in pks:
                poll = Poll.objects.get(pk=pk)
                poll.deleted = True
                poll.save()
                counter = counter + 1
    message =  u'Usunięto ' + unicode(counter) + u' ' + declination_poll(counter)
    messages.info(request, SafeUnicode(message))    
    return HttpResponseRedirect(reverse('grade-poll-list'))
    
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

@employee_required    
def questionset_create(request):
    data          = {}
    grade         = Semester.get_current_semester().is_grade_active
    data['grade'] = grade
    
    if grade:
        messages.error( request, "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona" )
        return HttpResponseRedirect('/news/grade')
    
    
    if request.method == "POST":
        # TODO:
        # Dodać tutaj wypełnienie forma danymi
        
        form_data = get_section_form_data( request.POST )
        errors    = validate_section_form( form_data )
        
        if errors:
            error_msg = u"Nie można utworzyć sekcji:\n<ul>"
            if errors.has_key( 'title' ):
                error_msg += u"<li>" + errors[ 'title' ] + u"</li>"
            if errors.has_key( 'content' ):
                error_msg += u"<li>" + errors[ 'content' ] + u"</li>"
            if errors.has_key( 'questions' ):
                question_errors = errors[ 'questions' ].keys()
                question_errors.sort()
                for position in question_errors:
                    error_msg += u"<li>Pytanie " + unicode(position) + ":\n<ul>"
                    for error in errors[ 'questions' ][ position ]:
                        error_msg += u"<li>" + error + u"</li>"
                    error_msg += u"</ul></li>"
            error_msg += u"</ul>"
            
            messages.error( request, SafeUnicode( error_msg ))
        else:
            if section_save( form_data ):
                messages.success( request, "Sekcja dodana" )
                return HttpResponseRedirect( '/grade/poll/managment/sections_list' )
            else:
                messages.error( request, "Zapis sekcji nie powiódł się" )
            
    return render_to_response ('grade/poll/section_create.html', data, context_instance = RequestContext( request ))

#### Poll answering ####
@login_required
def grade_logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('grade-poll-tickets-enter'))

def tickets_enter(request):
    grade = Semester.get_current_semester().is_grade_active
    data = {}
    
    if request.method == "POST":
        form = TicketsForm( request.POST, request.FILES )
        
        if form.is_valid():
            if request.FILES:
                keysfile = request.FILES[ 'ticketsfile' ]
                if keysfile.size > 1048576:
                    from django.template.defaultfilters import filesizeformat
                    messages.error( request, 
                        u'Proszę przesłać plik o maksymalnym rozmiarze: \
                        %s. Obecny rozmiar to: %s' % 
                        (filesizeformat(1048576), filesizeformat(keysfile.size)))
                    data[ 'form' ]  = form 
                    data[ 'grade' ] = grade
                    return render_to_response( 'grade/poll/tickets_enter.html', data, context_instance = RequestContext( request ))
                else:
                    tickets_plaintext = keysfile.read()
            else:
                tickets_plaintext = form.cleaned_data[ 'ticketsfield' ]
            try:
                ids_and_tickets   = from_plaintext( tickets_plaintext )
            except:
                ids_and_tickets   = []
            
            if not ids_and_tickets:
                messages.error( request, "Podano niepoprawne bilety." )
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
                        errors.append(( id, u"Nie udało się zweryfikować podpisu pod biletem." ))
                except:
                    errors.append(( id, u"Podana ankieta nie istnieje" ))

            if errors:
                msg = u"Wystąpił problem z biletami na następujące ankiety: <ul>"    
                for id, error in errors:
                    try:
                        poll = unicode( Poll.objects.get( pk = id ).title )
                    except:
                        poll = unicode( id )
                    msg += u'<li>' + poll + u'</li>'
                msg += u'</ul>'
                messages.error( request, SafeUnicode( msg ))
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
        return HttpResponseRedirect( reverse('grade-poll-tickets-enter') )
    
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
    data[ 'pid']        = pid
        
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
            form = PollForm( )
            form.setFields( poll, st, None, request.POST )
            
            errors = {}
            for key in request.POST:
                if key in form.fields:
                    if form.fields[ key ].type == 'multi':
                        field_data = request.POST.getlist( key )
                    else:
                        field_data = request.POST[ key ]
                    try:
                        form.fields[ key ].clean( field_data )
                    except ValidationError as ve:
                        errors[ key ] = ve.messages
            
            if errors:
                data[ 'form_errors' ] = errors
                messages.error(request, u"Nie udało się zapisać ankiety: " + poll.title + u"; błąd formularza")
            else:
                data[ 'form_errors' ] = {}
                keys = form.fields.keys()
                keys.remove( u'finish' )
                keys.sort()
                section_data = []
                
                if keys:
                    act     = [ keys[0] ]
                    curr_id = keys[0].split( '_' )[1].split( '-' )[1]
                    for key in keys[ 1: ]:
                        sect_id      = key.split( '_' )[1].split( '-' )[1]
                        if sect_id == curr_id:
                            act.append( key )
                        else:
                            section_data.append(( curr_id, act ))
                            curr_id = sect_id
                            act = [ key ]
                    if act: 
                        section_data.append(( curr_id, act ))
                
                for section_id, section_answers in section_data:
                    section = Section.objects.get( pk = section_id )
                    delete  = False
                    if section_answers[ 0 ].endswith( 'leading' ):
                        question_id = section_answers[ 0 ].split( '_' )[2].split( '-' )[ 1 ]
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
                        ansx = request.POST.get( section_answers[ 0 ], None)
                        if ansx:
                            option = Option.objects.get( pk = ansx)
                            print option
                            ans.option = option
                            ans.save()
                            print ans
                            if option in question.singlechoicequestionordering_set.filter( sections = section )[ 0 ].hide_on.all():
                                delete = True
                        else:
                            ans.delete()
                            delete = True
                        section_answers = section_answers[ 1: ]
                        
                    for answer in section_answers:
                        question_id   = answer.split( '_' )[2].split( '-' )[ 1 ]
                        question_type = answer.split( '_' )[2].split( '-' )[ 2 ]
                        if not answer.endswith( 'other' ):
                            if question_type == 'single':
                                question = SingleChoiceQuestion.objects.get( 
                                                pk = question_id )
                                try:
                                    ans = SingleChoiceQuestionAnswer.objects.get( 
                                                question     = question,
                                                saved_ticket = st ) 
                                except ObjectDoesNotExist:
                                    ans = SingleChoiceQuestionAnswer(
                                            section      = section,
                                            question     = question,
                                            saved_ticket = st )
                                    ans.save()
                                
                                value = request.POST.get( answer, None )
                                if delete: 
                                    ans.delete()
                                elif value:
                                    ans.option = Option.objects.get( pk = value )
                                    ans.save()
                                else:
                                    ans.delete()
                            if question_type == 'open':
                                question = OpenQuestion.objects.get( 
                                                pk = question_id )
                                try:
                                    ans = OpenQuestionAnswer.objects.get( 
                                                question     = question,
                                                saved_ticket = st ) 
                                except ObjectDoesNotExist:
                                    ans = OpenQuestionAnswer(
                                            section      = section,
                                            question     = question,
                                            saved_ticket = st )
                                    ans.save()
                                
                                value = request.POST.get( answer, None )
                                if delete: 
                                    ans.delete()
                                elif value:
                                    ans.content = value
                                    ans.save()
                                else:
                                    ans.delete()
                            if question_type == 'multi':
                                question = MultipleChoiceQuestion.objects.get( 
                                                pk = question_id )
                                try:
                                    ans = MultipleChoiceQuestionAnswer.objects.get( 
                                                question     = question,
                                                saved_ticket = st ) 
                                except ObjectDoesNotExist:
                                    ans = MultipleChoiceQuestionAnswer(
                                            section      = section,
                                            question     = question,
                                            saved_ticket = st )
                                    ans.save()
                                
                                value = request.POST.getlist( answer )
                                if delete: 
                                    ans.delete()
                                elif value:
                                    if u'-1' in value:
                                        ans.other = request.POST.get( answer + u'-other', None )
                                        value.remove( u'-1' )
                                    else:
                                        ans.other = None
                                    ans.options = []
                                    options = Option.objects.filter( pk__in = value )
                                    for option in options:
                                        ans.options.add( option )
                                    ans.save()
                                else:
                                    ans.delete()
                if request.POST.has_key( 'finish' ):
                    messages.success(request, u"Ankieta: " + poll.title + u" zakończona")
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
                    messages.success(request, u"Ankieta: " + poll.title + u" zapisana")
        else:
            form = PollForm()
            form.setFields( poll, st )

        data[ 'form' ]   = form
        
        if request.method == "POST" and (not data['form_errors'] or st.finished):
            print request.POST.get( 'Save', default=None )
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
    
    return HttpResponseRedirect( '/news/grade/' )
#### Poll results ####

@login_required
def poll_results( request, mode='S', poll_id = None ):
    ###
    # TODO:
    #   Filtry!!!
    
    data = {}
    data['grade'] = Semester.get_current_semester().is_grade_active
    
    if mode == 'S':
        data['mode']  = 'subject'
    elif mode == 'T':
        data['mode']  = 'teacher'
    
    semester      = Semester.get_current_semester()
    if semester.is_grade_active:
        messages.info( request, "Ocena zajęć jest otwarta; wyniki nie są kompletne." )
    
    if not poll_id:
        polls = filter( lambda x: x.is_user_entitled_to_view_result( request.user ), 
                                Poll.get_polls_for_semester())
        request.session['polls_by_subject'] = group_polls_by_subject( polls )
        request.session['polls_by_teacher'] = group_polls_by_teacher( polls )
    
    try:
        data['polls_by_subject'] = request.session['polls_by_subject']
        data['polls_by_teacher'] = request.session['polls_by_teacher']
    except:
        polls = filter( lambda x: x.is_user_entitled_to_view_result( request.user ), 
                                Poll.get_polls_for_semester())
        request.session['polls_by_subject'] = group_polls_by_subject( polls )
        request.session['polls_by_teacher'] = group_polls_by_teacher( polls )
        data['polls_by_subject']            = request.session['polls_by_subject']
        data['polls_by_teacher']            = request.session['polls_by_teacher']

        
    if poll_id:
        data['pid']       = poll_id
        poll              = Poll.objects.get( id = poll_id )
        data['link_mode'] = mode
        if poll.is_user_entitled_to_view_result( request.user ):
            poll_answers = poll.all_answers()
            sts_fin      = SavedTicket.objects.filter( poll = poll, finished = True  ).count()
            sts_not_fin  = SavedTicket.objects.filter( poll = poll, finished = False ).count()
            sts_all      = sts_fin + sts_not_fin

            answers = []
            for section, section_answers in poll_answers:
                s_ans = []
                for question, question_answers in section_answers:
                    if isinstance( question, SingleChoiceQuestion ):
                        mode     = u'single'
                        q_data   = map( lambda x: x.option, question_answers )
                        options  = question.options.all()
                        ans_data = []
                        for option in options:
                            ans_data.append(( option.content, q_data.count( option ), int(100 * (float(q_data.count( option )) / float(sts_fin)))))
                        ans_data.append((u"Brak odpowiedzi", sts_fin - len( q_data), int(100 * (float(sts_fin - len( q_data))/ float(sts_fin)))))
                        s_ans.append(( mode, question.content, ans_data, ( 100 / len( ans_data ))-1))
                        
                    elif isinstance( question, MultipleChoiceQuestion ):
                        mode               = u'multi'
                        q_data             = map( lambda x: (list( x.options.all()) , x.other), question_answers )
                        if q_data:
                            q_data, other_data = zip( *q_data )
                            q_data             = sum( q_data, [] )
                            other_data         = list( filter( lambda x: x, other_data ))
                        else:
                            other_data     = []
                        options            = question.options.all()
                        ans_data           = []
                        for option in options:
                            ans_data.append(( option.content, q_data.count( option ), int(100 * (float(q_data.count( option )) / float(sts_fin)))))
                        if question.has_other:
                            ans_data.append(( u"Inne", len( other_data ), int(100 * (float(len( other_data)) / float(sts_fin))), other_data))
                        ans_data.append((u"Brak odpowiedzi", sts_fin - len( question_answers), int(100 * (float(sts_fin - len(question_answers))/ float(sts_fin)))))
                        s_ans.append(( mode, question.content, ans_data, ( 100 / len( ans_data ))-1))
                        
                    elif isinstance( question, OpenQuestion ):
                        mode   = u'open'
                        q_data = map( lambda x: x.content, question_answers )
                        s_ans.append(( mode, question.content, q_data, len( q_data) ))
                        
                answers.append(( section.title, s_ans ))

            data['completness'] = SafeUnicode( u"Liczba studentów, którzy zakończyli wypełniać ankietę: %d<br/>Liczba studentów którzy nie zakończyli wypełniać ankiety: %d" % ( sts_fin, sts_not_fin ))
            data['poll_title']  = poll.title
            try:
                data[ 'poll_subject' ] = poll.group.subject.name
                data[ 'poll_group' ]   = poll.group.get_type_display()
                data[ 'poll_teacher' ] = poll.group.get_teacher_full_name()
            except:
                data[ 'poll_subject' ] = "Ankieta ogólna"
                
            try:
                user = poll.group.teacher
            except:
                user = None
                
            if user:
                if user == request.user:
                    data['show_share_toggle'] = True
            else:
                data['show_share_toggle'] = request.user.is_superuser
            
            data['share_state'] = poll.share_result
            data['results']     = answers
        else:
            messages.error( request, "Nie masz uprawnień do oglądania wyników tej ankiety." )
 
    return render_to_response ('grade/poll/poll_results.html', data, context_instance = RequestContext ( request ))

def share_results_toggle( request, mode, poll_id ):
    poll = Poll.objects.get( pk = poll_id )
    poll.share_result = not poll.share_result
    poll.save()
    if poll.share_result:
        messages.info( request, u"Udostępniono wyniki ankiety." )
    else:
        messages.info( request, u"Przestano udostepniać wyniki ankiety." )
    return HttpResponseRedirect(reverse( 'grade-poll-poll-results', args=[mode, poll_id] ))
