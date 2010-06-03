# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from offer.proposal.models.proposal_description_tag import ProposalDescriptionTag
          
PROPOSAL_TYPES = (
    ('seminar', 'Seminarium'),
    ('req',  'Obowiązkowy'),
    ('cs_1', 'Informatyczny'),
    ('cs_2', 'Informatyczny 2'),
)

PROPOSAL_HOURS = (
    (0, 0),
    (15, 15),
    (30, 30),
    (45, 45),
    (60, 60),
)

class ProposalDescription(models.Model):
    proposal = models.ForeignKey('Proposal', related_name = 'descriptions')
    description = models.TextField( verbose_name = 'opis' )
    requirements = models.TextField( verbose_name = 'wymagania' )
    comments = models.TextField( verbose_name = 'uwagi' )
    date = models.DateTimeField(verbose_name = 'data dodania')
    tags = models.ManyToManyField(ProposalDescriptionTag, blank = True)
    author = models.ForeignKey(User, related_name = 'autor')
    type = models.CharField(max_length = 30, choices = PROPOSAL_TYPES, 
        verbose_name = 'typ')
    ects = models.IntegerField(verbose_name ='sugerowana liczba punktów ECTS')
    lectures = models.IntegerField(verbose_name='ilość godzin wykładów', 
        choices = PROPOSAL_HOURS)
    repetitories = models.IntegerField(verbose_name='ilość godzin repetytoriów', 
        choices = PROPOSAL_HOURS)
    exercises = models.IntegerField(verbose_name='ilość godzin ćwiczeń', 
        choices = PROPOSAL_HOURS)
    laboratories = models.IntegerField(verbose_name='ilość godzin pracowni', 
        choices = PROPOSAL_HOURS)

    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotu'
        app_label = 'proposal'

    def __str__(self):
        return self.description

    def __unicode__(self):
        return self.description

    def getNewer( self, proposal ):
        nextDescription = ProposalDescription.objects.filter(
            proposal = proposal, 
            pk__gt = self.id)
        if nextDescription:
            return nextDescription[0]
        else:
            return None

    def getOlder( self, proposal ):
        description = ProposalDescription.objects.filter(proposal = proposal, 
                                                         pk__lt = self.id)
        if description:
            return description[description.count()-1]
        else:
            return None
    
    @staticmethod
    def get_by_tag(tag):
        "Return proposal descriptions by tag."
        return ProposalDescription.objects.filter(tags__name=tag)
    
    def add_tag(self, tag_name):
        """Apply tag to the proposal description."""
        try:
            tag = ProposalDescriptionTag.objects.get(name=tag_name) 
        except ProposalDescriptionTag.DoesNotExist:
            tag = ProposalDescriptionTag.objects.create(name=tag_name)
        finally:
            self.tags.add(tag)
    
    def remove_tag(self, tag_name):
        """Remove tag from the proposal description."""
        try:
            tag = ProposalDescriptionTag.objects.get(name=tag_name)
            self.tags.remove(tag)
        except ProposalDescriptionTag.DoesNotExist:
            pass
