# -*- coding: utf-8 -*-

from django.db import models

from fereol.offer.vote.models import SystemState

class SingleVote ( models.Model ):
    subject = models.ForeignKey  ( 'proposal.Proposal', 
                                   related_name = 'votes',
                                   verbose_name = 'przedmiot')

    value   = models.IntegerField( verbose_name = 'punkty')
    
    # ZMODYFIKOWAĆ SAVE'A I SETTERA ZAMIAST TEGO CO BYŁO...
    
    class Meta:
        verbose_name        = 'pojedynczy głos'
        verbose_name_plural = 'pojedyncze głosy'
        app_label           = 'vote'
        
        unique_together = ('subject', 'value')
        
    def __unicode__( self ):
        return self.subject.name + '; ' + str(self.value)
