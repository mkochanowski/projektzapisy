# -*- coding: utf8 -*-
from django.db     import models

from base_question          import BaseQuestion

class OpenQuestionOrdering( models.Model ):
    question = models.ForeignKey( 'OpenQuestion', verbose_name = 'pytanie' )
    section  = models.ForeignKey( 'Section', verbose_name = 'sekcja' )
    position = models.IntegerField( verbose_name = 'pozycja' )

    class Meta:
        verbose_name_plural = 'pozycje pytań otwartych'
        verbose_name        = 'pozycja pytań otwartych'
        ordering            = [ 'section', 'position' ]
        unique_together     = [ 'section', 'position' ]
        app_label           = 'poll' 
    
    def __unicode__( self ):
        return unicode( self.position ) + u'[' + unicode( self.section ) + u']' + unicode( self.question )
        
class OpenQuestion( BaseQuestion ):
    section = models.ManyToManyField( 'Section',    
                                      verbose_name = 'sekcje', 
                                      through = OpenQuestionOrdering )
    class Meta:
        abstract            = False
        verbose_name        = 'pytanie otwarte'
        verbose_name_plural = 'pytania otwarte'
        app_label           = 'poll'
