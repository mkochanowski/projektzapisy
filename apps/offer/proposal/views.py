# -*- coding: utf-8 -*-

"""
    Proposal views
"""
from django.core.exceptions import ObjectDoesNotExist

from datetime                       import datetime
from django.contrib                 import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.aggregates import Count
from django.http                    import Http404
from django.shortcuts               import render_to_response, get_object_or_404
from django.template                import RequestContext
from django.shortcuts               import redirect
from django.views.decorators.http   import require_POST
from apps.enrollment.courses.models.course_type import Type

from apps.offer.proposal.forms import ProposalForm, proposalFormset
from apps.offer.proposal.models          import Proposal, ProposalDescription
from apps.offer.proposal.exceptions      import NonStudentException, NonEmployeeException, NotOwnerException
from copy                           import deepcopy


import logging
from apps.offer.proposal.utils import prepare_proposals_data

logger = logging.getLogger("")


def main(request):
    return render_to_response( 'offer/main.html', {}, context_instance = RequestContext( request ))

@require_POST
@login_required
def become(request, slug, group):
    """
        Add user to group
    """
    try:
        try:
            if not request.user.is_staff:
                _ = request.user.employee
            proposal = Proposal.noremoved.get(slug=slug)
        except ObjectDoesNotExist:
            proposal = Proposal.filtred.get(slug=slug)
        proposal.add_user_to_group(request.user, group)
        return redirect("proposal-page" , slug=slug)
    except ObjectDoesNotExist:
        logger.error("Dodawanie uzytkownika do grupy przy proozycji. ObjectDoesNotExist. slug = %s" % slug)
        raise Http404
    except NonStudentException:
        logger.error("Dodawanie uzytkownika do grupy przy propozycji. NonStudentException. Id = %d" % proposal.id)
        request.user.message_set.create(message="Nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonEmployeeException:
        logger.error("Dodawanie uzytkownika do grupy przy propozycji. NonEmployeeException. Id = %d" % proposal.id)
        request.user.message_set.create(message="Nie jesteś pracownkiem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))

@require_POST
@login_required
def stop_be(request, slug, group):
    """
        Remove user from group
    """
    try:
        if request.user.employee:
            proposal = Proposal.noremoved.get(slug=slug)
        else:
            proposal = Proposal.filtred.get(slug=slug)
        proposal.delete_user_from_group(request.user, group)
        return redirect("proposal-page" , slug=slug)
    except ObjectDoesNotExist:
        logger.error("Usuwanie uzytkownika z grupy przy propozycji. ObjectDoesNotExist. slug = %s" % slug)
        raise Http404
    except NonStudentException:
        logger.error("Usuwanie uzytkownika z grupy przy propozycji. NonStudentException. Id = %d" % proposal.id)
        request.user.message_set.create(message="Nie jesteś studentem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
    except NonEmployeeException:
        logger.error("Usuwanie uzytkownika z grupy przy propozycji. NonEmployeeException. Id = %d" % proposal.id)
        request.user.message_set.create(message="Nie jesteś pracownkiem.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))


def proposals(request):
    """
        Proposal list
    """
    data               = prepare_proposals_data(request)
    data['types_list'] = Type.get_all_for_jsfilter()
    data['mode']       = 'list'
    
    return render_to_response( 'offer/proposal/base.html', data, context_instance = RequestContext(request) )

def proposal( request, slug, descid = None ):
    """
        Single proposal
    """
    try:
        try:
            if not request.user.is_staff:
                employee = request.user.employee
            proposal = Proposal.noremoved.get(slug=slug, deleted=False)
        except ObjectDoesNotExist:
            proposal = Proposal.filtred.get(slug=slug, deleted=False)

        newest         = proposal.description
        if descid:
            proposal.desc =  ProposalDescription.noremoved.get(id=descid)
        else:
            proposal.desc = newest

    except ObjectDoesNotExist:
        logger.error("Widok propozycji przedmiotu. ObjectDoesNotExist. slug = %s" % slug)
        raise Http404


    can_edit = (proposal.owner == None
               or request.user.is_staff
               or request.user == proposal.owner)


    data = prepare_proposals_data(request)
    data['proposal']  = proposal
    data['mode']      = 'details'
    data['newest']    = newest
    data['next']      = proposal.desc.get_newer()
    data['prev']      = proposal.desc.get_older()
    data['isFan']     = proposal.is_in_group(request.user, 'fans')
    data['isTeacher'] = proposal.is_in_group(request.user, 'teachers')
    data['isHelper']  = proposal.is_in_group(request.user, 'helpers')
    data['fans']      = proposal.fans_count()
    data['teachers']  = proposal.teachers_count()
    data['helpers']   = proposal.helpers_count()
    data['can_edit']  = can_edit
    

    return render_to_response( 'offer/proposal/view.html', data, context_instance = RequestContext( request ) )


@login_required
def proposal_form(request, slug=None ):
    """
        Form to add and edit proposal

    """
    form = ProposalForm(request, proposal_slug=slug)

    if slug:
        action = "zmieniona"
    else:
        action = "dodana"

    if form.saved:
        messages.success(request, "Propozycja została " + action)
        return redirect("proposal-page", slug )

    data          = prepare_proposals_data(request)
    data['forms'] = form.get_forms()

    return render_to_response( 'offer/proposal/form.html', data, context_instance = RequestContext(request));

@login_required
def proposal_history( request, slug ):
    """
        Edition history
    """
    proposal = get_object_or_404(Proposal, slug = slug, deleted = False)
    can_edit = (proposal.owner == None
               or request.user.is_staff
	       or proposal.owner == request.user)

    data                 = prepare_proposals_data(request)
    data['descriptions'] = proposal.descriptions_set.order_by( '-date' ).filter(deleted = False)
    data['can_edit']     = can_edit
    
    
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
    
    logger.debug('Przywrocenie opisu o id = %d' % int(descid))
    newdesc             = deepcopy(olddesc)
    newdesc.id          = None
    newdesc.author      = request.user
    newdesc.save()

    olddesc.proposal.description = newdesc
    olddesc.proposal.description.save()

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
    description = ProposalDescription.noremoved.get(id=pid)
    how_many    = ProposalDescription.noremoved.filter(proposal = description.proposal).count()
    if (how_many == 1):
       description.proposal.deleted = True
       description.proposal.save()
    else:
        description.proposal.description = description.get_older()
        description.proposal.save()
    description.deleted = True

    description.save()    
    messages.success(request, "Opis został usunięty")

    if (how_many > 1):
        return redirect("proposal-page", description.proposal.slug )
    else:
        messages.info(request, "Usunięto również przedmiot")
        return redirect("proposal-list")
 
@permission_required('proposal.can_create_offer')
def offer_create( request ):
    """
        Widok listy przedmiotów, które można wybrać w ramach oferty dydaktycznej
    """

    query = Proposal.noremoved.all().annotate(num_fans=Count('fans'),
                                              num_teachers=Count('teachers'),
                                              num_helpers=Count('helpers'))

    if request.POST:
        proposals = proposalFormset( request.POST, queryset=query )
        if proposals.is_valid():
            messages.success(request, "Zmieniono stan oferty")
            proposals.save()
    else:
        proposals = proposalFormset( queryset=query )
    data = {
        'proposals' : proposals,
    }    
    
    return render_to_response('offer/proposal/create_offer.html', data, context_instance = RequestContext( request ))

@login_required
def get_group(request,group, id):
    proposal = Proposal.filtred.get( pk = id, deleted = False)

    if group == 'Fans':
        users = proposal.fans.all()
    elif group == 'Teachers':
        users = proposal.teachers.all()
    else:
        users = proposal.helpers.all()

    return render_to_response('offer/proposal/users_group.html', {'users':users}, context_instance = RequestContext( request ))
