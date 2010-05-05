# -*- coding: utf-8 -*-

from django.db import models

MAX_VOTE = 3

class SingleVote ( models.Model ):
    VALUE_CHOICES = [ (x, str(x)) for x in range(1, MAX_VOTE+1) ]
                
    subject = models.ForeignKey  ( 'proposal.Proposal', 
                                   related_name = 'votes',
                                   verbose_name = 'przedmiot' )
    value   = models.IntegerField( verbose_name = 'punkty',
                                   choices      = VALUE_CHOICES)
    class Meta:
        verbose_name        = 'pojedynczy głos'
        verbose_name_plural = 'pojedyncze głosy'
        app_label           = 'vote'
        
    def __unicode__( self ):
        return self.subject.name + '; ' + str(self.value)
   
class Votes ( models.Model ):
    user    = models.ForeignKey ( 'users.Student',
                                  related_name = 'votes',
                                  verbose_name = 'głosujący')
    votes   = models.ManyToManyField( SingleVote )
    year    = models.DateField(   verbose_name = 'data głosowania' )
    
    class Meta:
        verbose_name        = 'głos'
        verbose_name_plural = 'głosy'
        app_label           = 'vote'

    def __unicode__( self ):
        return u'Głos użytkownika: ' + self.user.user.username
