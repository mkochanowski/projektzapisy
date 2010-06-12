# -*- coding: utf-8 -*-

"""
    Description of proposal
"""

from django.db import models
from django.contrib.auth.models import User

from offer.proposal.models.proposal_description_tag import ProposalDescriptionTag
          
PROPOSAL_TYPES = (
    ('seminar', 'Seminarium'),
    ('req',  'Obowiązkowy'),
    ('cs_1', 'Informatyczny I'),
    ('cs_2', 'Informatyczny II'),
)

PROPOSAL_HOURS = (
    (0, 0),
    (15, 15),
    (30, 30),
    (45, 45),
    (60, 60),
)


class ProposalDescription(models.Model):
    """
        Description of proposal
    """
    proposal = models.ForeignKey('Proposal', related_name = 'descriptions')
    description  = models.TextField( verbose_name = 'opis' )
    requirements = models.TextField( verbose_name = 'wymagania' )
    comments     = models.TextField( verbose_name = 'uwagi' )
    
    date         = models.DateTimeField(verbose_name = 'data dodania')
    tags         = models.ManyToManyField(ProposalDescriptionTag, blank = True)
    author       = models.ForeignKey(User, related_name='autor')
    
    type         = models.CharField(max_length = 30, choices = PROPOSAL_TYPES, 
                                     verbose_name = 'typ')
    ects         = models.IntegerField(verbose_name ='sugerowana liczba punktów ECTS')
    
    lectures     = models.IntegerField(verbose_name = 'ilość godzin wykładów', 
                                            choices = PROPOSAL_HOURS)
    repetitories = models.IntegerField(verbose_name = 'ilość godzin repetytoriów', 
                                            choices = PROPOSAL_HOURS)
    exercises    = models.IntegerField(verbose_name = 'ilość godzin ćwiczeń', 
                                            choices = PROPOSAL_HOURS)
    laboratories = models.IntegerField(verbose_name =' ilość godzin pracowni', 
                                            choices = PROPOSAL_HOURS)
    deleted = models.BooleanField(verbose_name='usunięty', default=False)
    
    web_page = models.CharField( verbose_name = 'Strona WWW', 
                                max_length   = 200,
                                blank        = True,
                                null         = True )
                                
    
    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotu'
        app_label = 'proposal'

    def __unicode__(self):
        return '[' + self.author.__unicode__() + ']' + self.proposal.name 

    def get_newer( self, proposal ):
        """
            Gets next description (by date) if exists
        """
        description = ProposalDescription.objects.filter(
                                                proposal = proposal, 
                                                pk__gt   = self.id)
        if description:
            return description[0]
        else:
            return None

    def get_older( self, proposal ):
        """
            Gets previous description (by date) if exists
        """
        description = ProposalDescription.objects.filter(proposal = proposal, 
                                                         pk__lt = self.id)
        if description:
            return description[description.count()-1]
        else:
            return None
    
    @staticmethod
    def get_by_tag(tag):
        """
            Return proposal descriptions by tag.
        """
        return ProposalDescription.objects.filter(tags__name=tag)
    
    def add_tag(self, tag_name):
        """
            Apply tag to the proposal description.
        """
        try:
            tag = ProposalDescriptionTag.objects.get(name=tag_name) 
        except ProposalDescriptionTag.DoesNotExist:
            tag = ProposalDescriptionTag.objects.create(name=tag_name)
        finally:
            self.tags.add(tag)
    
    def remove_tag(self, tag_name):
        """
            Remove tag from the proposal description.
        """
        try:
            tag = ProposalDescriptionTag.objects.get(name=tag_name)
            self.tags.remove(tag)
        except ProposalDescriptionTag.DoesNotExist:
            pass

