# -*- coding: utf-8 -*-
from django.http                         import HttpResponse
from django.shortcuts                    import render_to_response
from django.template                     import RequestContext

from fereol.users.decorators             import student_required
from fereol.enrollment.subjects.models   import Semester, \
                                                Group,\
                                                Subject
                                                
from fereol.enrollment.records.models    import Record

from fereol.grade.ticket_create.utils    import generate_keys_for_polls, \
                                                split_groups_by_subject, \
                                                generate_ticket, \
                                                secure_signer, \
                                                unblind, \
                                                get_valid_tickets, \
                                                to_plaintext

from fereol.grade.ticket_create.forms    import GroupCombineForm

from fereol.grade.ticket_create.exceptions import *

def prepare_grade( request ):
    return render_to_response( 'grade/ticket_create/prepare_grade.html', {}, context_instance = RequestContext( request ))
        
def keys_generate( request ):   
    generate_keys_for_polls( )
    return render_to_response( 'grade/ticket_create/prepare_grade.html', { 'msg': 'Wygenerowano klucze RSA' }, context_instance = RequestContext( request ))

@student_required
def connections_choice( request ):
    # TODO:
    #   1. Brać bez grup oczekujących
    #   2. Brać tylko grupy z tego semestru
    record_groups   = Record.objects.filter( student = request.user.student )
    record_groups   = record_groups.values_list( 'group', flat = True )
    student_groups  = Group.objects.filter( pk__in = record_groups ).order_by( 'subject' )
    
    groups_by_subjects = split_groups_by_subject( student_groups )
    
    if request.method == "POST":
        form = GroupCombineForm( request.POST, 
                                 groups_by_subject = groups_by_subjects )
         
        if form.is_valid():
            connected_groups = []
            for groups in groups_by_subjects:
                sub_key = Subject.objects.get( name = groups[ 0 ].subject.name ).pk
                if   len( groups ) == 1:
                    connected_groups.append( groups )
                elif form.cleaned_data[ 'connect_' + unicode( sub_key )]:
                    connected_groups.append( groups )
                else:
                    for group in groups:
                        connected_groups.append( [group] )
            
            request.method = "GET"
            tickets = reduce(list.__add__, 
                             map( lambda gs: generate_ticket( gs ), 
                                  connected_groups ))
            return tickets_save( request, tickets )
    else:
        form = GroupCombineForm( groups_by_subject = groups_by_subjects )
        
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
             'tickets' : to_plaintext( tickets_to_serve ) }
             
    return render_to_response( "grade/ticket_create/tickets_save.html", data, context_instance = RequestContext( request ))
