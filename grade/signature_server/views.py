# -*- coding: utf-8 -*-
from django.http                         import HttpResponse
from django.shortcuts                    import render_to_response
from django.template                     import RequestContext
from fereol.users.decorators             import student_required, \
                                                employee_required
from fereol.enrollment.records.models    import Record
from fereol.enrollment.subjects.models   import Group, \
                                                Subject
from fereol.grade.signature_server.utils import check_and_sign, \
                                                prepare_groups, \
                                                group_list_to_group_connection, \
                                                generate_ticket, \
                                                signature_preparer
from fereol.grade.signature_server.forms import GroupChooseForm
@student_required
def get_tickets_for_grade(request): 
    record_groups   = Record.objects.filter( student = request.user.student )
    record_groups   = record_groups.values_list( 'group', flat = True )
    student_groups  = Group.objects.filter( pk__in = record_groups ).order_by( 'subject' )
    prepared_groups = prepare_groups( student_groups )
    # dodać filtrowanie tak, żeby grupy były z tego semestru..
    # i tak, żeby nie brać oczekujących!
    data = {}
    forms = []
    if request.method == "POST":
        for key in prepared_groups.keys():
            forms.append( GroupChooseForm( request.POST, subject = key, subject_groups = prepared_groups[ key ]))
            
        if all( [ f.is_valid() for f in forms ] ):
            choosed_groups = {}
            for form in forms:
                for key in form.cleaned_data.keys():
                    if form.cleaned_data[ key ]:
                        [ sub_pk, group_pk, i ] = map( int, key.split( '_' ) )
                        sub_name = Subject.objects.get( pk = sub_pk   ).name
                        group    = Group.objects.get(   pk = group_pk )
                        if choosed_groups.has_key( sub_name ):
                            choosed_groups[ sub_name ].append( group )
                        else:
                            choosed_groups[ sub_name ] = [ group ]
            
            choosed_group_connections = []
            for key in choosed_groups.keys():
                choosed_group_connections.append( group_list_to_group_connection( choosed_groups[ key ]))
            list_of_tickets = map( lambda gc: generate_ticket( request.user, gc ), choosed_group_connections )
            
            request.method = "GET"
            #~ data[ 'p' ] = list_of_tickets
            return generate_tickets_sign( request, list_of_tickets )
    else:
        for key in prepared_groups.keys():
            forms.append( GroupChooseForm( subject = key, subject_groups = prepared_groups[ key ]))
        
    
    data[ 'forms' ] = forms
        
    return render_to_response ('grade/signature_server/tickets_choice.html', data, context_instance = RequestContext ( request ))
    
@student_required
def generate_tickets_sign( request, list_of_tickets ):
    data = { 'tickets': signature_preparer( request.user, list_of_tickets )}
    return render_to_response ('grade/signature_server/generate_tickets.html', data, context_instance = RequestContext ( request ))
        
