# -*- coding: utf-8 -*-

from django.db import models

from singleVote import SingleVote

class Votes ( models.Model ):
    user    = models.ForeignKey ( 'users.Student',
                                  related_name = 'votes',
                                  verbose_name = 'głosujący')
    votes   = models.ManyToManyField( SingleVote )
    
    class Meta:
        verbose_name        = 'głos'
        verbose_name_plural = 'głosy'
        app_label           = 'vote'

    def __unicode__( self ):
        return u'Głos użytkownika: ' + self.user.user.username
