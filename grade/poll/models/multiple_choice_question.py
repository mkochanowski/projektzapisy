# -*- coding: utf8 -*-
from django.db     import models

from base_question import BaseQuestion
from option        import Option

class MultipleChoiceQuestion( BaseQuestion ):    
    section = models.ManyToManyField( 'Section',    
                                      verbose_name = 'sekcje', 
                                      through = 'MultipleChoiceQuestionOrdering' )
    has_other    = models.BooleanField(    verbose_name = 'opcja inne' )
    choice_limit = models.IntegerField(    verbose_name = 'maksimum opcji do wyboru' )
    options      = models.ManyToManyField( Option, 
                                           verbose_name = 'odpowiedzi' ) 
    
    class Meta:
        verbose_name_plural = 'pytania wielokrotnego wyboru'
        verbose_name        = 'pytanie wielokrotnego wyboru'
        app_label           = 'poll'
        abstract            = False


class MultipleChoiceQuestionOrdering( models.Model ):
    question = models.ForeignKey( MultipleChoiceQuestion, 
                                  verbose_name = 'pytanie' )
    section  = models.ForeignKey( 'Section', verbose_name = 'sekcja' )
    position = models.IntegerField( verbose_name = 'pozycja' )
    
    class Meta:
        verbose_name_plural = 'pozycje pytań wielokrotnego wyboru'
        verbose_name        = 'pozycja pytań wielokrotnego wyboru'
        ordering            = [ 'section', 'position' ]
        unique_together     = [ 'section', 'position' ]
        app_label           = 'poll' 
    
    def __unicode__( self ):
        return unicode( self.position ) + u'[' + unicode( self.section ) + u']' + unicode( self.question )
