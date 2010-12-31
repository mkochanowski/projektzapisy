# -*- coding: utf8 -*-
from django.db import models

from poll      import Poll

class Section( models.Model ):
    title       = models.CharField( max_length = 50,  verbose_name = 'tytuł' )
    description = models.TextField( blank = True, verbose_name = 'opis' ) 
    poll        = models.ManyToManyField( Poll, verbose_name = 'ankieta',
                                          through = 'SectionOrdering' )
    
    class Meta:
        verbose_name        = 'sekcja'
        verbose_name_plural = 'sekcje'
        app_label           = 'poll'
        
    def __unicode__( self ):
        return unicode( self.title )
        
    def all_questions( self ):
        pass
        
    def save( self ):
        super( Section, self).save()

class SectionOrdering( models.Model ):
    poll     = models.ForeignKey( Poll,      verbose_name = 'ankieta' )
    section  = models.ForeignKey( Section, verbose_name = 'sekcja' )
    position = models.IntegerField( verbose_name = 'pozycja' )

    class Meta:
        verbose_name_plural = 'pozycje sekcji'
        verbose_name        = 'pozycja sekcji'
        ordering            = [ 'poll', 'position' ]
        unique_together     = [ 'poll', 'position' ]
        app_label           = 'poll'
