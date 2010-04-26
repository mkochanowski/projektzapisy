# -*- coding: utf-8 -*-

from django.db import models

from proposal_description_tag import ProposalDescriptionTag

class ProposalDescription(models.Model):
    proposal = models.ForeignKey('Proposal', related_name = 'descriptions')
    description = models.TextField( verbose_name = 'opis' )
    date = models.DateTimeField(verbose_name = 'data dodania')
    tags = models.ManyToManyField(ProposalDescriptionTag)
    
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
            return description[0]
        else:
            return None
    
    @staticmethod
    def get_by_tag(tag):
        "Return proposal descriptions by tag."
        return ProposalDescription.objects.filter(tags__name=tag)
