# -*- coding: utf-8 -*-

import datetime
import fereol.offer.proposal.models 

from django.contrib.auth.decorators import login_required, permission_required
from django.http                    import HttpResponse
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.shortcuts               import redirect

from fereol.enrollment.records.models          import *
from fereol.offer.proposal.models              import *

@login_required
def become_fan(request, slug):
    try:
        proposal = Proposal.objects.get(slug=slug)
        proposal.addUserToFans(request.user)
        return redirect("proposal-page" , slug=slug)
    except NonStudentException:
        request.user.message_set.create(message="Nie jesteś studentem")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except NonEmployeeException:
        request.user.message_set.create(message="Nie jesteś pracownkiem")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
        
@login_required
def become_teacher(request, slug):
    try:
        proposal = Proposal.objects.get(slug=slug)
        proposal.addUserToTeachers(request.user)
        return redirect("proposal-page" , slug=slug)
    except NonStudentException:
        request.user.message_set.create(message="Nie jesteś studentem")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except NonEmployeeException:
        request.user.message_set.create(message="Nie jesteś pracownkiem")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))

@login_required
def stop_be_fan(request, slug):
    try:
        proposal = Proposal.objects.get(slug=slug)
        proposal.deleteUserFromFans(request.user)
        return redirect("proposal-page" , slug=slug)
    except NonStudentException:
        request.user.message_set.create(message="Nie jesteś studentem")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except NonEmployeeException:
        request.user.message_set.create(message="Nie jesteś pracownkiem")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))

@login_required
def stop_be_teacher(request, slug):
    try:
        proposal = Proposal.objects.get(slug=slug)
        proposal.deleteUserFromTeachers(request.user)
        return redirect("proposal-page" , slug=slug)
    except NonStudentException:
        request.user.message_set.create(message="Nie jesteś studentem")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))
    except NonEmployeeException:
        request.user.message_set.create(message="Nie jesteś pracownkiem")
        return render_to_response('errorpage.html', context_instance=RequestContext(request))

@login_required
def proposals(request):
    proposals = Proposal.objects.all()
    return render_to_response( 'offer/proposal/proposal_list.html',
        {
            'proposals' : proposals,
            'mode' : 'list'
        }, context_instance = RequestContext(request) )

@login_required
def proposal( request, slug, descid = None ):
    proposal = Proposal.objects.get(slug=slug)
    newest = proposal.description()
    if descid:
        proposal.description = ProposalDescription.objects.get( pk = descid )
    else:
        proposal.description = newest
        descid = proposal.description.id
        
    next = proposal.description.getNewer( proposal )
    prev = proposal.description.getOlder( proposal )

    data = {
            'proposal'      : proposal,
            'mode'          : 'details',            
            'proposals'     : Proposal.objects.all(),
            'descid'        : int(descid),
            'newest'        : newest,
            'id'            : proposal.id,
            'next'          : next,
            'prev'          : prev,
            'isFan'         : proposal.isFan(request.user),
            'isTeacher'     : proposal.isTeacher(request.user),
            'fans'          : proposal.fansCount(),
            'teachers'      : proposal.teachersCount(),
    }
    return render_to_response( 'offer/proposal/proposal_list.html', data, context_instance = RequestContext( request ) )


def proposal_form(request, sid = None):
    """
        Formularz do dodawania i edycji przedmiotu.
    """
    editMode = True if sid else False    
    message = None
    booksToForm = []
    success = False
    proposalDescription = ""
    proposalRequirements = ""
    proposalComments = ""
    
    proposal = None
    if editMode:
        try:
            proposal = Proposal.objects.get(pk = sid)
            proposalDescription = proposal.description().description 
            proposalRequirements = proposal.description().requirements
            proposalComments = proposal.description().comments
        except:            
            editMode = False
    
    if request.method == 'POST':        
        if not editMode:
            proposal = Proposal()
            
        correctForm = True
        
        """ Read data from html form """
        
        proposalName = request.POST.get('name', '')
        proposalDescription = request.POST.get('description', '')
        proposalRequirements = request.POST.get('requirements', '')
        proposalComments = request.POST.get('comments', '')
        
        proposalType = request.POST.get('type', '')
        
        try:
            proposalEcts = int(request.POST.get('ects', 0))
        except:
            proposalEcts = ""

        proposalLectures = int(request.POST.get('lectures', -1))
        proposalRepetitories = int(request.POST.get('repetitories', -1))
        proposalExercises = int(request.POST.get('exercises', -1))
        proposalLaboratories = int(request.POST.get('laboratories', -1))        
        
        books = request.POST.getlist('books[]')
        
        proposal.name = proposalName
        proposal.slug = proposal.createSlug(proposal.name)
                
        proposal.type = proposalType
        proposal.ects = proposalEcts
        proposal.lectures = proposalLectures
        proposal.repetitories = proposalRepetitories
        proposal.exercises = proposalExercises
        proposal.laboratories = proposalLaboratories                
        
        if Proposal.objects.filter(slug = proposal.slug).exclude(id = proposal.id).count() > 0:                
            message = 'Istnieje już przedmiot o takiej nazwie'
            correctForm = False                                                 
            
        if  (proposalName == "" or proposalEcts == "" or proposalDescription == ""
            or proposalRequirements == "" or proposalType == ""
            or proposalLectures == -1 or proposalRepetitories == -1
            or proposalExercises == -1 or proposalLaboratories == -1):
            message = ('Podaj nazwę, opis, wymagania, typ przedmiotu, liczbę ' +
                'punktów ECTS oraz liczbę godzin zajęć.')
            correctForm = False
                                
        if correctForm:
                        
            proposal.save()
            
            description = ProposalDescription()
            description.description = proposalDescription
            description.requirements = proposalRequirements
            description.comments = proposalComments
            description.date = datetime.now()
            description.proposal = proposal
            description.save()
            
            bookOrder = request.POST['bookOrder'].split(';')
            newBooksOrder = []
            oldBooksOrder = {}            
            newBookCounter = 0
            orderNumber = 1            
                        
            for order in bookOrder:
                if order == '_':
                    if books[newBookCounter] != "":                                                   
                        newBooksOrder.append(orderNumber)
                        orderNumber += 1
                        
                    newBookCounter += 1
                else:
                    book = request.POST.get('book' + str(order), None)
                    if book:
                        oldBooksOrder[int(order)] = orderNumber
                        orderNumber += 1                        
            
            for book in proposal.books.all():
                fieldValue =  request.POST.get('book' + str(book.id), None)                                                
                if fieldValue != None:
                    if fieldValue == "":                    
                        book.delete()
                    else:
                        book.name = fieldValue
                        book.order = oldBooksOrder[book.id]                        
                        book.save()
                                                                       
          
            newBookCounter = 0
            for bookName in books:
                if bookName != "":
                    book = Book(name = bookName, proposal = proposal, order = newBooksOrder[newBookCounter]).save()                
                    newBookCounter += 1
                                        
                    
            success = True                                     
                                               
            if editMode:
                message = 'Zmiany zostały wprowadzone.'
            else:
                message = 'Przedmiot został dodany.'
        
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
        'proposalDescription'   : proposalDescription,
        'proposalRequirements'  : proposalRequirements,
        'proposalComments'      : proposalComments,
        'mode'          : 'form',
        'proposals'     : Proposal.objects.all(),
        'proposalTypes' : fereol.offer.proposal.models.proposal.PROPOSAL_TYPES,
        'proposalHours' : fereol.offer.proposal.models.proposal.PROPOSAL_HOURS,
    }
    
    if success:
        return redirect("proposal-page" , slug=proposal.slug)
    else:
        return render_to_response( 'offer/proposal/proposal_list.html', data, context_instance = RequestContext(request));

@login_required
def proposal_history( request, sid ):
    proposal      = Proposal.objects.get( pk = sid)
    descriptions = proposal.descriptions.order_by( '-date' )
    data         = { 'descriptions' : descriptions }
    
    return render_to_response ('offer/proposal/proposal_history.html', data, context_instance = RequestContext(request)) 
    
@login_required
def proposal_view_archival( request, descid ):
    desc = ProposalDescription.objects.get( pk = descid )
    data = {'desc' : desc}
    
    return render_to_response ('offer/proposal/proposal_archival.html', data)
    
@login_required
def proposal_restore ( request, descid ):
    olddesc             = ProposalDescription.objects.get( pk = descid )
    newdesc             = ProposalDescription()
    newdesc.description = olddesc.description
    newdesc.requirements = olddesc.requirements
    newdesc.comments    = olddesc.comments
    newdesc.date        = datetime.now()
    newdesc.proposal    = olddesc.proposal
    newdesc.save()
    
    return proposal( request, olddesc.proposal.slug )

@permission_required('proposal.can_create_offer')
def offerCreate( request ):
    """
        Widok listy przedmiotów, które można wybrać w ramach oferty dydaktycznej
    """
    data = {
        'subjects' : Proposal.objects.order_by('name'),
    }    
    
    return render_to_response('offer/proposal/offerCreate.html', data, context_instance = RequestContext( request ))
    
@permission_required('proposal.can_create_offer')
def offerCreateTeachers( request, subjectId ):
    """
        Widok pobiera listę nauczycieli gotowych poprowadzić dany przedmiot.
        TODO: zrobić pobieranie listy
    """
    data = {
        'teachers' : []
    }
    return render_to_response('offer/proposal/offerCreateTeachers.html', context_instance = RequestContext( request ))

@permission_required('proposal.can_create_offer')
def offerSelect(request):
    """
        Wybiera lub odznacza przedmiot w ofercie dydaktycznej
    """    
    action = request.POST['action']
    id = request.POST['id']
    
    proposal = Proposal.objects.get(pk = id)
    
    if action == 'select':
        proposal.add_tag("offer")
    else: # unselect
        proposal.remove_tag("offer")
        
    return HttpResponse('ok')
