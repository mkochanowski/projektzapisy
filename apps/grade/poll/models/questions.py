# -*- coding: utf-8 -*-

"""
    Question and answers
"""

from django.db import models

class Answer( models.Model ):
    """
        Represents answer
    """
    contents = models.TextField( verbose_name = "treść" )
    
    class Meta:
        verbose_name        = "odpowiedź"
        verbose_name_plural = "odpowiedzi"
        app_label           = "poll"
        
    def __unicode__( self ):
        if len(self.contents) > 50:
            return self.contents[:50] + "..."
        else:
            return self.contents

class Question( models.Model ):
    """
        Abstract class for question
    """
    contents    = models.TextField( verbose_name = "treść" )
    description = models.TextField( verbose_name = "opis" )
    required    = models.BooleanField( verbose_name = "obowiązkowe" )
    reason      = models.BooleanField( verbose_name = "uzasadnienie" )
    
    class Meta:
        verbose_name        = "pytanie"
        verbose_name_plural = "pytania"
        app_label           = "poll"
        abstract            = True
    
    def __unicode__( self ):
        return self.contents

class OpenQuestion( Question ):
    """
        Open question
    """
    class Meta:
        verbose_name        = "pytanie otwarte"
        verbose_name_plural = "pytania otwarte"
        app_label           = "poll"
        
class SingleChoiceQuestion( Question ):
    """
        Question with single answer
    """
    answers = models.ManyToManyField( Answer, 
                                      verbose_name = "odpowiedzi" )
    has_other = models.BooleanField( verbose_name = "inna odpowedź" )
    
    class Meta:
        verbose_name        = "pytanie jednokrotnego wyboru"
        verbose_name_plural = "pytania jednokrotnego wyboru"
        app_label           = "poll"
        
class MultipleChoiceQuestion( Question ):
    """
        Question with multiple answers
    """
    answers = models.ManyToManyField( Answer, 
                                      verbose_name = "odpowiedzi" )
    has_other = models.BooleanField( verbose_name = "inna odpowedź" )
    
    class Meta:
        verbose_name        = "pytanie wielokrotnego wyboru"
        verbose_name_plural = "pytania wielokrotnego wyboru"
        app_label           = "poll"
