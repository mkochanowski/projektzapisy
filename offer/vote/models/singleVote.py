# -*- coding: utf-8 -*-

from django.db import models

from fereol.offer.vote.models import SystemState

MAX_VOTE = SystemState.get_maxPoints()

class SingleVote ( models.Model ):
    VALUE_CHOICES = [ (x, str(x)) for x in range(1, MAX_VOTE+1) ]
                
    subject = models.ForeignKey  ( 'proposal.Proposal', 
                                   related_name = 'votes',
                                   verbose_name = 'przedmiot')
    value   = models.IntegerField( verbose_name = 'punkty',
                                   choices      = VALUE_CHOICES)
    
    class Meta:
        verbose_name        = 'pojedynczy głos'
        verbose_name_plural = 'pojedyncze głosy'
        app_label           = 'vote'
        
        unique_together = ('subject', 'value')
        
    def __unicode__( self ):
        return self.subject.name + '; ' + str(self.value)
