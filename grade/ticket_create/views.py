# -*- coding: utf-8 -*-
from django.http                         import HttpResponse
from django.shortcuts                    import render_to_response
from django.template                     import RequestContext

from fereol.users.decorators             import student_required
from fereol.enrollment.subjects.models   import Semester, \
                                                Group,\
                                                Subject
from fereol.enrollment.records.models    import Record
from fereol.grade.poll.models            import Poll
from fereol.grade.ticket_create.utils    import generate_keys_for_polls, \
                                                group_polls_by_subject, \
                                                generate_ticket, \
                                                secure_signer, \
                                                unblind, \
                                                get_valid_tickets, \
                                                to_plaintext

from fereol.grade.ticket_create.forms    import PollCombineForm

from fereol.grade.ticket_create.exceptions import *

def prepare_grade( request ):
    return render_to_response( 'grade/ticket_create/prepare_grade.html', {}, context_instance = RequestContext( request ))
        
def keys_generate( request ):   
    generate_keys_for_polls()
    return render_to_response( 'grade/ticket_create/prepare_grade.html', { 'msg': 'Wygenerowano klucze RSA' }, context_instance = RequestContext( request ))

@student_required
def connections_choice( request ):
    students_polls = Poll.get_all_polls_for_student( request.user.student )
    groupped_polls = group_polls_by_subject( students_polls )
    
    if request.method == "POST":
        form = PollCombineForm( request.POST, 
                                polls = groupped_polls )
         
        if form.is_valid():
            connected_groups = []
            for polls in groupped_polls:
                if not polls[ 0 ].group:
                    label = 'join_common'
                else:
                    label = u'join_' + unicode( polls[ 0 ].group.subject.pk )
                
                if len( polls ) == 1:
                    connected_groups.append( polls )
                elif form.cleaned_data[ label ]:
                    connected_groups.append( polls )
                else:
                    for poll in polls:
                        connected_groups.append([ poll ])
            
            request.method = "GET"
            tickets = reduce(list.__add__, 
                             map( lambda gs: generate_ticket( gs ), 
                                  connected_groups ))
            return tickets_save( request, tickets )
    else:
        form = PollCombineForm( polls = groupped_polls )
        
    data = { 'form' : form }
    return render_to_response ('grade/ticket_create/connection_choice.html', data, context_instance = RequestContext ( request ))
    
@student_required
def tickets_save( request, ticket_list ):
    signed = map( lambda ( g, t, ( m, k )): 
                        (g, t, secure_signer( request.user, g, t ), (m, k)),
                  ticket_list )
    
    prepared_tickets = map ( lambda ( g, t, st, ( m, k ) ): 
                                (g, m, unblind( g, st, k ) ),
                             signed )
 
    errors, tickets_to_serve = get_valid_tickets( prepared_tickets )

    data = { 'errors'  : errors,
             'tickets' : to_plaintext( tickets_to_serve )}
             
    return render_to_response( "grade/ticket_create/tickets_save.html", data, context_instance = RequestContext( request ))
