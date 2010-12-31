# -*- coding: utf8 -*-
from django.db     import models

from base_question import BaseQuestion
from option        import Option
from section       import Section
    
class SingleChoiceQuestion( BaseQuestion ):
    section = models.ManyToManyField( Section,    verbose_name = 'sekcje', 
                                      through = 'SingleChoiceQuestionOrdering' )
                                      
    is_scale = models.BooleanField(    verbose_name = 'skala' )
    options  = models.ManyToManyField( Option, 
                                       verbose_name = 'odpowiedzi' )
    
    class Meta:
        verbose_name_plural = 'pytania jednokrotnego wyboru'
        verbose_name        = 'pytanie jednokrotnego wyboru'
        app_label           = 'poll'
        abstract            = False

class SingleChoiceQuestionOrdering( models.Model ):
    question   = models.ForeignKey( SingleChoiceQuestion, 
                                    verbose_name = 'pytanie' )
    section    = models.ForeignKey( Section, verbose_name = 'sekcja' )
    position   = models.IntegerField( verbose_name = 'pozycja' )
    is_leading = models.BooleanField( verbose_name = 'pytanie wiodące' )
    hide_on    = models.ManyToManyField( Option,
                                         verbose_name = 'ukryj sekcję przy \
                                                         odpowiedziach' )
    class Meta:
        verbose_name_plural = 'pozycje pytań jednokrotnego wyboru'
        verbose_name        = 'pozycja pytań jednokrotnego wyboru'
        ordering            = [ 'section', 'is_leading', 'position' ]
        unique_together     = [ 'section', 'is_leading', 'position' ]
        app_label           = 'poll' 
