# -*- coding: utf-8 -*-
from django.contrib                      import messages
from django.http                         import HttpResponse, HttpResponseRedirect
from django.shortcuts                    import render_to_response
from django.template                     import RequestContext
from django.utils                        import simplejson
from apps.users.decorators             import student_required, employee_required
from django.contrib.auth.decorators      import login_required

from apps.enrollment.subjects.models   import Semester, \
                                                Group,\
                                                Subject
from apps.enrollment.records.models    import Record
from apps.grade.poll.models            import Poll
from apps.grade.ticket_create.utils    import generate_keys_for_polls, \
                                                generate_keys,          \
                                                group_polls_by_subject, \
                                                secure_signer, \
                                                unblind, \
                                                get_valid_tickets, \
                                                to_plaintext, \
                                                connect_groups, \
                                                secure_signer_without_save, \
                                                secure_mark
from apps.grade.ticket_create.forms      import PollCombineForm
from apps.grade.ticket_create.exceptions import *
from apps.grade.ticket_create.models     import PublicKey
from django.contrib.auth                   import authenticate, login, logout
from apps.grade.ticket_create.forms      import *
from django.views.decorators.csrf          import csrf_exempt
from Crypto.PublicKey import RSA
from django.core.cache import cache


### KEYS generate:

@employee_required
def ajax_keys_generate( request ):
    generate_keys_for_polls()
    return HttpResponse("OK")
    
@employee_required
def ajax_keys_progress( request ):
    count = cache.get('generated-keys', 0)
    return HttpResponse(str(count))

@employee_required
def keys_generate( request ):   
    grade = Semester.get_current_semester().is_grade_active
    if grade:
        messages.error( request, "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona" )
        return HttpResponseRedirect( '/news/grade' )
    count = Poll.get_current_semester_polls_without_keys().all().count()
    return render_to_response( 'grade/ticket_create/keys_generate.html', { 'grade' : grade, 'keys': count }, context_instance = RequestContext( request ))

@student_required
def ajax_get_rsa_keys_step1( request ):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            students_polls = Poll.get_all_polls_for_student( request.user.student )
            groupped_polls = group_polls_by_subject( students_polls )
            form = PollCombineForm( request.POST, 
                                    polls = groupped_polls )
            if form.is_valid():
                connected_groups = connect_groups( groupped_polls, form )
                tickets = map( lambda gs: generate_keys( gs ), 
                                      connected_groups ) 
                message = simplejson.dumps(tickets)
    return HttpResponse(message)

@student_required
def ajax_get_rsa_keys_step2( request ):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            students_polls = Poll.get_all_polls_for_student( request.user.student )
            groupped_polls = group_polls_by_subject( students_polls )
            form = PollCombineForm( request.POST, 
                                    polls = groupped_polls )
            if form.is_valid():
                ts               = simplejson.loads( request.POST.get('ts') )
                connected_groups = connect_groups( groupped_polls, form )
                groups           = reduce(list.__add__, connected_groups )
                tickets          = zip( groups, ts)
                signed = map( lambda ( g, t): 
                            (g, long(t), secure_signer_without_save( request.user, g, long(t) )),
                             tickets )
                unblinds = map ( lambda ( g, t, st ): 
                                (unicode(t), unblind( g, st ) ),
                             signed )
                message = simplejson.dumps(unblinds)
    return HttpResponse(message)

@student_required
def connections_choice( request ):
    grade = Semester.get_current_semester().is_grade_active
    students_polls = Poll.get_all_polls_for_student( request.user.student )
    groupped_polls = group_polls_by_subject( students_polls )
    
    if grade:
        if request.method == "POST":
            form = PollCombineForm( request.POST, 
                                    polls = groupped_polls )
             
            if form.is_valid():
                unblindst = simplejson.loads( request.POST.get('unblindst', '') )
                unblindt  = simplejson.loads( request.POST.get('unblindt', '') )
                ts        = simplejson.loads( request.POST.get('ts', '') )
                connected_groups = connect_groups( groupped_polls, form)
                groups           = reduce(list.__add__, connected_groups )
                prepared_tickets = zip( groups, unblindt, unblindst )
                #### final mark:
    
                for g, t, unblind in prepared_tickets:
                    secure_mark(request.user, g, t )
    
                errors, tickets_to_serve = get_valid_tickets( prepared_tickets )
                data = { 'errors'  : errors,
                         'tickets' : to_plaintext( tickets_to_serve ),
                         'grade' : grade }
                return render_to_response( "grade/ticket_create/tickets_save.html", data, context_instance = RequestContext( request ))
                
        else:
            form = PollCombineForm( polls = groupped_polls )
            
        data = { 'form' : form, 'grade' : grade}
        return render_to_response ('grade/ticket_create/connection_choice.html', data, context_instance = RequestContext ( request ))
    else:
        return render_to_response ('grade/ticket_create/connection_choice.html', {'grade': grade, 'error': "Ocena zajęć jest w tej chwili zamknięta; nie można pobrać biletów"}, context_instance = RequestContext ( request ))
    

@csrf_exempt
def client_connection( request ):
    if request.method == 'POST':
        
        form = ContactForm(request.POST)
        
        if form.is_valid():
            idUser = form.cleaned_data['idUser']
            passwordUser = form.cleaned_data['passwordUser']
            groupNumber = form.cleaned_data['groupNumber']
            groupKey = long(form.cleaned_data['groupKey'])
        
            user = authenticate(username=idUser, password=passwordUser)

            if user:
                pass
            else:
                return HttpResponse(u"nie ma takiego użytkownika")


            if groupNumber == u"*":
                st=u""
                students_polls = Poll.get_all_polls_for_student( user.student )
                groupped_polls = group_polls_by_subject( students_polls )
                for polls in groupped_polls:
                    
                    if len( polls ) == 1:
                        
                        st += unicode( polls[0].pk ) + u'***'
                        st += u'[' + unicode( polls[0].title ) + u']%%%'
            
                        if polls[0].group:
                            st += unicode( polls[0].group.subject.name ) + u'%%%'
                            st += unicode( polls[0].group.get_type_display()) + u': %%%'
                            st += unicode( polls[0].group.get_teacher_full_name()) + u'%%%'

                        st +=unicode( '***' )
                            
                        st += unicode( PublicKey.objects.get( poll = polls[0].pk ).public_key ) + u'???'
                        
                    else:
                        for poll in polls:
                            st += unicode( poll.pk ) + u'***'
                            if not poll.group:
                                st += u'Ankiety ogólne: %%%   [' + poll.title + '] '
                            else:
                                st += u'Przedmiot: ' + polls[ 0 ].group.subject.name + u'%%%    [' + poll.title + u'] ' + \
                                         poll.group.get_type_display() + u': ' + \
                                         poll.group.get_teacher_full_name() + u'***'
                                st += unicode( PublicKey.objects.get( poll = poll.pk ).public_key ) + '&&&'
                        st += u'???'

                return HttpResponse( st )

            
            students_polls = Poll.get_all_polls_for_student( user.student )

            st = ""
            
            for students_poll in students_polls:
                if int(students_poll.pk) == int(groupNumber):
                    
                    st = secure_signer_without_save( user, students_poll, groupKey)
                    secure_signer( user, students_poll, groupKey )
                    p = students_poll
                    break
            if st == "":
                st = u"Nie jesteś zapisany do tej ankiety"


            try:
                a=long(st[0][0])
            except ValueError, err:
                return HttpResponse(st)
            if   st == u"Nie jesteś zapisany do tej ankiety":
                return HttpResponse(st)
            elif st == u"Bilet już pobrano":
                return HttpResponse(st)
            else:
                return HttpResponse( to_plaintext( [(p,u'***',u'%%%')] ) + u'???' + unicode(a) )

            
@csrf_exempt
def keys_list( request ):
    l = PublicKey.objects.all()#.order_by('poll__group__subject__name')
    return render_to_response('grade/ticket_create/keys_list.html', {'list': l,},context_instance = RequestContext( request ))
