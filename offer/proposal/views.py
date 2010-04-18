# -*- coding: utf-8 -*-

import datetime
import re

from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.shortcuts               import redirect

from fereol.enrollment.records.models          import *
from fereol.offer.proposal.models              import *

@login_required
def proposals(request):
    proposals = Proposal.objects.all()
    return render_to_response( 'offer/proposal/proposal_list.html', { 'proposals' : proposals, 'mode' : 'list' }, context_instance = RequestContext(request) )

@login_required
def proposal( request, slug ):
    proposal = Proposal.objects.get(slug=slug)
    data = {
            'proposal'       : proposal,
            'mode'          : 'details',
            'proposals'      : Proposal.objects.all()             
    }         
    return render_to_response( 'offer/proposal/proposal_list.html', data, context_instance = RequestContext( request ) )


def proposalForm(request, sid = None):
    """
        Formularz do dodawania i edycji przedmiotu.
    """
    editMode = True if sid else False    
    message = None
    booksToForm = []
    success = False
    proposalDescription = ""
    
    proposal = None
    if editMode:
        try:
            proposal = Proposal.objects.get(pk = sid)
            proposalDescription = proposal.description().description 
        except:            
            editMode = False
    
    if request.method == 'POST':        
        if not editMode:
            proposal = Proposal()
            
        correctForm = True
        
        """ Read data from html form """
        
        proposalName = request.POST.get('name', '')
        proposalDescription = request.POST.get('description', '')
        
        books = request.POST.getlist('books[]')
        
        proposal.name = proposalName
        proposal.slug = proposal.createSlug(proposal.name)        
        
        if Proposal.objects.filter(slug = proposal.slug).exclude(id = proposal.id).count() > 0:                
            message = 'Istnieje już przedmiot o takiej nazwie'
            correctForm = False                                    
            
        if proposalName == "" or proposalDescription == "":
            message = 'Wypełnij wszystkie pola'
            correctForm = False
                                
        if correctForm:
                        
            proposal.save()
            
            description = ProposalDescription()
            description.description = proposalDescription
            description.date = datetime.datetime.now()
            description.proposal = proposal
            description.save()
            
            for book in proposal.books.all():
                fieldValue =  request.POST.get('book' + str(book.id), None)                                                
                if fieldValue != None:
                    if fieldValue == "":                    
                        book.delete()
                    elif book.name != fieldValue:
                        book.name = fieldValue
                        book.save()                                                
          
            for bookName in books:
                if bookName != "":
                    book = Book(name = bookName, proposal = proposal).save()
                    
            success = True                                     
                                               
            if editMode:
                message = 'Zmiany zostały wprowadzone'
            else:
                message = 'Przedmiot został dodany'
                proposal = None
                proposalDescription = ""
        
    if proposal and proposal.id:
        booksToForm = list(proposal.books.all())
        
        
    if request.method == "POST" and not success:
        for bookName in request.POST.getlist('books[]'):
            booksToForm.append({ "id" : None, "name" : bookName})
    
    
    data = {
        'editForm'  : True,
        'editMode'  : editMode,
        'message'   : message,
        'proposal'  : proposal,
        'books'     : booksToForm,
        'proposalDescription' : proposalDescription,
        'mode'      : 'form',
        'proposals'  : Proposal.objects.all()
    }
    return render_to_response( 'offer/proposal/proposal_list.html', data, context_instance = RequestContext(request));

@login_required
def proposalHistory( request, sid ):
    proposal      = Proposal.objects.get( pk = sid)
    descriptions = proposal.descriptions.order_by( '-date' )
    data         = { 'descriptions' : descriptions }
    
    return render_to_response ('offer/proposal/proposal_history.html', data, context_instance = RequestContext(request)) 
    
@login_required
def proposalViewArcival( request, descid ):
    desc = ProposalDescription.objects.get( pk = descid )
    data = {'desc' : desc}
    
    return render_to_response ('offer/proposal/proposal_archival.html', data)
    
@login_required
def proposalRestore ( request, descid ):
    olddesc = ProposalDescription.objects.get( pk = descid )
    newdesc             = ProposalDescription()
    newdesc.description = olddesc.description
    newdesc.date        = datetime.datetime.now()
    newdesc.Proposal     = olddesc.Proposal
    newdesc.save()
    
    return Proposal( request, olddesc.Proposal.slug )
