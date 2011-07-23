# -*- coding: utf-8 -*-

"""
    Proposal views
"""

import apps.offer.proposal.models

from datetime                       import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.http                    import HttpResponse
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.shortcuts               import redirect
from django.views.decorators.http   import require_POST
from django.contrib                 import messages
from copy                           import deepcopy

from apps.users.models            import Program

from apps.offer.proposal.models          import Proposal, Book, ProposalDescription, DescriptionTypes
from apps.enrollment.courses.models                 import Type
from apps.offer.proposal.exceptions      import NonStudentException, NonEmployeeException, NotOwnerException


import logging
logger = logging.getLogger("")

def main(request):
    return render_to_response( 'offer/base.html', {}, context_instance = RequestContext( request ))

@require_POST
@login_required
def become(request, slug, group):
    """
        Add user to group
    """
    try:
        proposal_ = Proposal.objects.get(slug=slug)
        proposal_.add_user_to_group(request.user, group)
        return redirect("proposal-page" , slug=slug)
    except NonStudentException:
        logger.error("Dodawanie uzytkownika do grupy przy propozycji. NonStudentException. Id = %d" % proposal_.id)
        request.user.message_set.create(message="Nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonEmployeeException:
        logger.error("Dodawanie uzytkownika do grupy przy propozycji. NonEmployeeException. Id = %d" % proposal_.id)
        request.user.message_set.create(message="Nie jesteś pracownkiem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@require_POST
@login_required
def stop_be(request, slug, group):
    """
        Remove user from group
    """
    try:
        proposal_ = Proposal.objects.get(slug=slug)
        proposal_.delete_user_from_group(request.user, group)
        return redirect("proposal-page" , slug=slug)
    except NonStudentException:
        logger.error("Usuwanie uzytkownika z grupy przy propozycji. NonStudentException. Id = %d" % proposal_.id)
        request.user.message_set.create(message="Nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonEmployeeException:
        logger.error("Usuwanie uzytkownika z grupy przy propozycji. NonEmployeeException. Id = %d" % proposal_.id)
        request.user.message_set.create(message="Nie jesteś pracownkiem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@login_required
def proposals(request):
    """
        Proposal list
    """
    proposals_ = Proposal.objects.filter(deleted=False).order_by('name')
    return render_to_response( 'offer/proposal/base.html',
        {
            'proposals' : proposals_,
            'mode' : 'list'
        }, context_instance = RequestContext(request) )

@login_required
def proposal( request, slug, descid = None ):
    """
        Single proposal
    """
    proposal_ = Proposal.objects.get(slug=slug, deleted=False)
    newest   = proposal_.description()

    if descid:
        proposal_.description = ProposalDescription.objects.get( pk = descid )
    else:
        proposal_.description = newest
        descid = proposal_.description.id

    can_edit = (proposal_.owner == None 
               or request.user.is_staff
               or request.user == proposal_.owner)
    proposals_ = Proposal.objects.filter(deleted=False).order_by('name')
    data = {
            'proposal'      : proposal_,
            'mode'          : 'details',            
            'proposals'     : proposals_,
            'descid'        : int(descid),
            'newest'        : newest,
            'id'            : proposal_.id,
            'next'          : proposal_.description.get_newer( proposal_ ),
            'prev'          : proposal_.description.get_older( proposal_ ),
            'isFan'         : proposal_.is_in_group(request.user, 'fans'),
            'isTeacher'     : proposal_.is_in_group(request.user, 'teachers'),
            'isHelper'      : proposal_.is_in_group(request.user, 'helpers'),
            'fans'          : proposal_.fans_count(),
            'teachers'      : proposal_.teachers_count(),
            'helpers'       : proposal_.helpers_count(),
            'can_edit'      : can_edit,
            'types'         : proposal_.description.descriptiontypes.all()
    }
    return render_to_response( 'offer/proposal/view.html', data, context_instance = RequestContext( request ) )

@login_required
def proposal_form(request, sid = None):
    """
        Form to add and edit proposal

    """

    """

    proposal = Proposal.objects.get_or_404(id=sid) # sid = description id??


    if 'cancel' in request.POST:
        redirect show

    if request.POST:
        form = ProposalCreator(request=request)

        if form.save():
            commit
            messages.success(request, "Udalo sie")
            redirect show
        else:
            rollback
            messages.error(request, "Nie udalo sie")

    else:
        form = ProposalCreator(instance=proposal)

    data = {}
    data['form'] = form
    return render_to_response( 'offer/proposal/form.html', data, context_instance = RequestContext(request));

    """

    edit_mode = True if sid else False    
    books_to_form = []
    success = False
    proposal_description = ""
    proposal_requirements = ""
    proposal_comments = ""
    proposal_www = ""
    types_name = Type.get_types()

    types_table = {}

    for type_name in types_name:
        types_table[type_name.id] = type_name

    proposal_ = None
    if edit_mode:
        try:
            proposal_ = Proposal.objects.get(pk = sid)
            proposal_description = proposal_.description().description 
            proposal_requirements = proposal_.description().requirements
            proposal_comments = proposal_.description().comments
            proposal_www      = proposal_.description().web_page
            if proposal_.is_exam(): proposal_exam   = 'yes' 
            else:                   proposal_exam   = 'no'
            if proposal_.in_english(): proposal_english = 'yes' 
            else:                      proposal_english = 'no'
        
        except:            
            edit_mode = False
    
    if request.method == 'POST':        
        if not edit_mode:
            proposal_ = Proposal()
            
        correct_form = True
        
        # Read data from html form 
        
        proposal_name = request.POST.get('name', '')
        proposal_description = request.POST.get('description', '')
        proposal_requirements = request.POST.get('requirements', '')
        proposal_comments = request.POST.get('comments', '')
        proposal_owner = request.POST.get('owner', 'no')
        proposal_www = request.POST.get('web-page', '')
        proposal_exam = request.POST.get('exam', 'no')
        proposal_english = request.POST.get('classes-in-english', 'no')
        
        if (proposal_owner == "yes"
           and proposal_.owner == None):
            proposal_.owner = request.user
        
        if (proposal_.owner != None
           and proposal_.owner != request.user
           and not request.user.is_staff):
            raise NotOwnerException
        
        if proposal_owner == "no":
            proposal_.owner = None

        try:
            proposal_ects = int(request.POST.get('ects', 0))
        except:
            proposal_ects = ""

        proposal_lectures = int(request.POST.get('lectures', -1))
        proposal_repetitories = int(request.POST.get('repetitories', -1))
        proposal_seminars = int(request.POST.get('seminars', -1))
        proposal_exercises = int(request.POST.get('exercises', -1))
        proposal_laboratories = int(request.POST.get('laboratories', -1))        
        
        books = request.POST.getlist('books[]')
        types = request.POST.getlist('types[]')

        proposal_.name = proposal_name
        proposal_.slug = proposal_.create_slug(proposal_.name)             
        
        if Proposal.objects.filter(slug = proposal_.slug).exclude(id = proposal_.id).count() > 0:                
            request.user.message_set.create(message='Istnieje już przedmiot o takiej nazwie.')
            correct_form = False                                                 

        if proposal_.slug == '':
            request.user.message_set.create(message='Nazwa przedmiotu jest niepoprawna.')
            correct_form = False

        number_of_types = 0
        for one_type in types:
            if one_type != "":
                number_of_types = number_of_types + 1

        if  ( proposal_name == "" or proposal_ects == "" or proposal_description == ""
            or proposal_requirements == "" or proposal_lectures == -1
            or proposal_repetitories == -1 or proposal_seminars == -1
            or proposal_exercises == -1 or proposal_laboratories == -1):
                request.user.message_set.create(message=\
                    'Podaj nazwę, opis, wymagania, typ przedmiotu, liczbę ' + \
                    'punktów ECTS oraz liczbę godzin zajęć.')
                correct_form = False
        
        if correct_form:
            
            proposal_.save()
 
            if proposal_exam == 'yes':
                proposal_.add_tag('exam')
            else:
                proposal_.remove_tag('exam')
                
            if proposal_english == 'yes':
                proposal_.add_tag('english')
            else:
                proposal_.remove_tag('english')
        
            description = ProposalDescription()
            description.author = request.user
            description.description = proposal_description
            description.requirements = proposal_requirements
            description.ects = proposal_ects
            description.lectures = proposal_lectures
            description.repetitories = proposal_repetitories
            description.seminars = proposal_seminars
            description.exercises = proposal_exercises
            description.laboratories = proposal_laboratories
            description.web_page = proposal_www   
            description.comments = proposal_comments
            description.date = datetime.now()
            description.proposal = proposal_
            description.save()

            
            
            if edit_mode:                
                logger.debug('Edycja propozycji przedmiotu id = %d, %s' % (proposal_.id, proposal_.name))
            else:
                logger.debug('Dodanie propozycji przedmiotu id = %d, %s' % (proposal_.id, proposal_.name))
                
                        

            # to tutaj można sobie pooszczędzać na usuwanych obiektach
            # (patrz TODO kilkadziesiąt linijek wyżej)
            for book in proposal_.books.all():
                book.delete()

            new_book_counter = 0
            for book_name in books:
                if book_name != "":
#                    book = Book(name = book_name, proposal = proposal, order = newBooksOrder[new_book_counter]).save()
                    Book(name = book_name, proposal = proposal_, order = new_book_counter).save()
                    new_book_counter += 1
                                        
            for type_id in types:
                if type_id != "":
                    DescriptionTypes(description = description, lecture_type = types_table[int(type_id)]).save()

            success = True                                     
                                               
            if edit_mode:
                request.user.message_set.create(message=\
                    'Zmiany zostały wprowadzone.')
            else:
                request.user.message_set.create(message=\
                    'Przedmiot został dodany.')
    
    if proposal_ and proposal_.id:
        books_to_form = list(proposal_.books.all())
        types = proposal_.description().descriptiontypes.all()
    else:
        types = None
        
    if request.method == "POST" and not success:
        for book_name in request.POST.getlist('books[]'):
            books_to_form.append({ "id" : None, "name" : book_name})

    proposals_ = Proposal.objects.filter(deleted=False).order_by('name')
    try:
        exam = proposal_.is_exam()
    except ValueError:
        exam = False
    except AttributeError:
        exam = False
        
    try:
        english = proposal_.in_english()
    except ValueError:
        english = False
    except AttributeError:
        english = False
    
    data = {
        'editForm'              : True,
        'editMode'              : edit_mode,
        'proposal'              : proposal_,
        'books'                 : books_to_form,
        'proposalDescription'   : proposal_description,
        'proposalRequirements'  : proposal_requirements,
        'proposalComments'      : proposal_comments,
        'proposalWWW'           : proposal_www,
        'exam'                  : exam,
        'english'               : english,
        'mode'                  : 'form',
        'proposals'             : proposals_,
        'proposalHours'         : apps.offer.proposal.models.proposal_description.PROPOSAL_HOURS,
        'types'                 : types,
        'typesName'             : types_name
    }
    
    if success:
        return redirect("proposal-page" , slug=proposal_.slug)
    else:
        return render_to_response( 'offer/proposal/form.html', data, context_instance = RequestContext(request));

@login_required
def proposal_history( request, sid ):
    """
        Edition history
    """
    proposal_ = Proposal.objects.get( pk = sid, deleted = False)
    can_edit = (proposal_.owner == None
               or request.user.is_staff
	       or proposal_.owner == request.user)

    data = {
        'descriptions' : proposal_.descriptions.order_by( '-date' ).filter(deleted = False),
        'proposals'    : Proposal.objects.filter(deleted=False).order_by('name'),
        'can_edit'     : can_edit
    }
    
    return render_to_response ('offer/proposal/history.html', data, context_instance = RequestContext(request)) 
    
@login_required
@require_POST
def proposal_restore ( request, descid ):
    """
        Description restore
    """
    olddesc             = ProposalDescription.objects.get( pk = descid, deleted=False )

    if (olddesc.proposal.owner != None
       and not request.user.is_staff
       and request.user != olddesc.proposal.owner):
        logger.error('NotOwnerException przy przywracaniu opisu o id = %d' % descid)
        raise NotOwnerException
    
    logger.debug('Przywrocenie opisu o id = %d' % descid)
    newdesc             = deepcopy(olddesc)
    newdesc.id          = None
    newdesc.date        = datetime.now()
    newdesc.author      = request.user
    newdesc.save()
    
    for proposal_type in olddesc.descriptiontypes.all():
        DescriptionTypes(description = newdesc, lecture_type = proposal_type.lecture_type).save()

    return redirect("proposal-page", olddesc.proposal.slug )

@require_POST
@permission_required('proposal.can_delete_proposal')
def delete_proposal( request, slug ):
    """
       Usuwamy dana propozycje
    """    
    proposal = Proposal.objects.get(slug=slug)
    logger.debug('Usuniecie propozycji przedmiotu id = %d, %s' % (proposal.id, proposal.name))
    proposal.deleted = True
    proposal.save()        
    
    return redirect("proposal-list")

@require_POST
@permission_required('proposal.can_delete_proposal')
def delete_description( request, pid ):
    """
       Usuwamy dany opis
    """
    description = ProposalDescription.objects.get(id=pid)
    how_many    = ProposalDescription.objects.filter(proposal = description.proposal, deleted=False).count()
    if (how_many == 1):
       description.proposal.deleted = True
       description.proposal.save()
    description.deleted = True
    description.save()    
    request.user.message_set.create(message="Opis został usunięty.")

    if (how_many > 1):
        return redirect("proposal-page", description.proposal.slug )
    else:
        return redirect("proposal-list")
 
@permission_required('proposal.can_create_offer')
def offer_create( request ):
    """
        Widok listy przedmiotów, które można wybrać w ramach oferty dydaktycznej
    """
    if request.method == "POST":
        courses = map( int, request.POST.getlist('courses[]'))

        for id in courses:
            proposal = Proposal.objects.get(pk = id, deleted = False)
            action = int( request.POST.get('course[' + str(id) + ']', 0) )
            proposal.remove_tag('summer')
            proposal.remove_tag('winter')
            if action == 0:
                proposal.remove_tag('offer')
                proposal.remove_tag('vote')
            elif action == 1:
                proposal.add_tag('offer')
                proposal.remove_tag('vote')
            else:
                proposal.add_tag('vote')
                proposal.add_tag('offer')
                semester =  request.POST.get('course_semester[' + str(id) + ']', 'brak')
                
                if semester == 'letni':
                    proposal.add_tag('summer')
                elif semester == 'zimowy':
                    proposal.add_tag('winter')

        messages.success(request, 'Zmieniono stan oferty')

    all_courses = Proposal.objects.filter(deleted=False).order_by('name')
    vote_list  = Proposal.get_pks_by_tag('vote')
    offer_list = Proposal.get_pks_by_tag('offer')

    summer_list = Proposal.get_pks_by_tag('summer')
    winter_list = Proposal.get_pks_by_tag('winter')
    
    for course in all_courses:
        if course.id in vote_list:
            course.state = 'vote'
        elif course.id in offer_list:
            course.state = 'offer'
        else:
            course.state = 'none'

        if course.id in summer_list:
            course.semester = 'summer'
        elif course.id in winter_list:
            course.semester = 'winter'
        else:
            course.semester = 'none'
            
    data = {
        'courses' : all_courses,
    }    
    
    return render_to_response('offer/proposal/create_offer.html', data, context_instance = RequestContext( request ))

@login_required
def get_group(request,group, id):
    proposal = Proposal.objects.get( pk = id, deleted = False)

    if group == 'Fans':
        users = proposal.fans.all()
    elif group == 'Teachers':
        users = proposal.teachers.all()
    else:
        users = proposal.helpers.all()

    return render_to_response('offer/proposal/users_group.html', {'users':users}, context_instance = RequestContext( request ))
