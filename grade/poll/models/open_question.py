# -*- coding: utf8 -*-
from django.db     import models

from base_question          import BaseQuestion
from section                import Section

class OpenQuestionOrdering( models.Model ):
    question = models.ForeignKey( 'OpenQuestion', verbose_name = 'pytanie' )
    section  = models.ForeignKey( Section,        verbose_name = 'sekcja' )
    position = models.IntegerField( verbose_name = 'pozycja' )

    class Meta:
        verbose_name_plural = 'pozycje pytań otwartych'
        verbose_name        = 'pozycja pytań otwartych'
        ordering            = [ 'section', 'position' ]
        unique_together     = [ 'section', 'position' ]
        app_label           = 'poll' 
        
class OpenQuestion( BaseQuestion ):
    section = models.ManyToManyField( Section,    verbose_name = 'sekcje', 
                                      through = OpenQuestionOrdering )
    class Meta:
        abstract            = False
        verbose_name        = 'pytanie otwarte'
        verbose_name_plural = 'pytania otwarte'
        app_label           = 'poll'
