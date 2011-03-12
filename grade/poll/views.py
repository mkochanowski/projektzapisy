# -*- coding: utf-8 -*-

from django.http                import HttpResponse
from django.shortcuts           import render_to_response
from django.template            import RequestContext

from fereol.grade.poll.forms    import KeysForm
from fereol.users.decorators    import student_required, employee_required

from fereol.grade.poll.crypto   import validate_key, \
                                       link_name
                                                     # TODO: 
                                                     #      być może to trzeba będzie
                                                     #      zrobić w osobnej apce

@employee_required
def create( request ):
    # TODO:
    #       Obsługa formularza
    return render_to_response ('grade/poll/add.html', context_instance = RequestContext( request ))

@student_required
def get_keys( request ):
    # TODO:
    #       Pobieranie kluczy
    #       Tu musi być podpięcie do kryptografii i generowania
    pass
    
def check_keys( request ):
    data = {}
    if request.method == "POST":
        form = KeysForm( request.POST )
        data['form'] = form
        
        if form.is_valid():
            keys = form.cleaned_data[ 'keysfield' ]
            
            cands = keys.split( '\n' )
            links = []
            
            for key in cands:
                if validate_key( key ):
                # TODO:
                #       Prawdziwa weryfikacja kluczy
                #       Tu musi być podpięcie do kryptografii i weryfikacji
                    links.append( (key, link_name( key ) ) )
                    
            return render_to_response ('grade/poll/form_links.html', { 'links' : links }, context_instance = RequestContext ( request ))
    else:
        form = KeysForm()
        data['form'] = form        
    
    return render_to_response ('grade/poll/keys_verify.html', data, context_instance = RequestContext ( request ))

def default( request ):
    return render_to_response ('grade/poll/main.html', context_instance = RequestContext ( request ))

