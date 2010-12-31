# -*- coding: utf8 -*-
from django.db                import models
from fereol.grade.poll.models import Poll

class PublicKey( models.Model ):
    poll       = models.ForeignKey( Poll, verbose_name = 'ankieta' )
    public_key = models.TextField(  verbose_name = 'klucz publiczny' )
    
    class Meta:
        verbose_name        = 'klucz publiczny'
        verbose_name_plural = 'klucze publiczne'
        app_label           = 'ticket_create'
        
    def __unicode__( self ):
        return u"Klucz publiczny: " + unicode( self.poll )
