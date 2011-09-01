# -*- coding: utf-8 -*-
from django.forms.models import ModelForm, inlineformset_factory, modelformset_factory
from django.shortcuts import get_object_or_404
from apps.offer.proposal.models.book import Book
from apps.offer.proposal.models.proposal import Proposal
from apps.offer.proposal.models.proposal_description import ProposalDescription


class MainProposalForm(ModelForm):

    class Meta:
        fields = ('name',)
        model  = Proposal




class DescriptionForm(ModelForm):
    def save(self, proposal=None, author=None):
        description = super(DescriptionForm, self).save(commit=False)
        description.id       = None
        description.author   = author
        description.proposal = proposal
        description.date     = None
        description.save()

        return description

    class Meta:
        fields = ('description', 'requirements', 'comments', 'web_page', 'type', 'exam', 'english')
        model  = ProposalDescription
        

BookForm = inlineformset_factory(ProposalDescription, Book, fields=('name',), can_delete=False)
        

class ProposalForm(object):

    def __init__(self, request, proposal_slug=None):

        self.request = request
        self.saved   = False
        proposal     = Proposal()
        description  = ProposalDescription()
        
        if proposal_slug:
            proposal    = get_object_or_404(Proposal, slug=proposal_slug)
            description = proposal.description()


        if request.method == 'POST':
            self.proposal    = MainProposalForm( request.POST, prefix='proposal', instance=proposal )
            self.description = DescriptionForm( request.POST, prefix='description', instance=description )
            self.books       = BookForm( request.POST, prefix='books', instance=description )
            self.save()

        else:
            self.proposal    = MainProposalForm( instance=proposal, prefix='proposal' )
            self.description = DescriptionForm( instance=description, prefix='description' )
            self.books       = BookForm( prefix='books', instance=description )


    def get_forms(self):
        return {
            'proposal':    self.proposal,
            'description': self.description,
            'books':       self.books
        }

    def save(self):
            if self.proposal.is_valid():
                proposal = self.proposal.save()

                if self.description.is_valid():
                    if self.books.is_valid():
                        description = self.description.save(proposal=proposal,
                                          author=self.request.user)
                        books = self.books.save(commit=False)
                        for book in books:
                            book.id = None
                            book.proposal_description = description
                            book.save()

                        self.saved=True
                        proposal.description = description
                        proposal.save()
                        
                else:
                    self.books.is_valid()

            else:
                self.description.is_valid()
                self.books.is_valid()


proposalFormset = modelformset_factory(Proposal, fields=('status', 'semester', 'for_student'), extra=0)
