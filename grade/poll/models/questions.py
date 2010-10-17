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
        app_label           = "grade"
        
    def __unicode__( self ):
        return self.contents

class Question( models.Model ):
    """
        Abstract class for question
    """
    contents = models.TextField( verbose_name = "treść" )
    
    class Meta:
        verbose_name        = "pytanie"
        verbose_name_plural = "pytania"
        app_label           = "grade"
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
        app_label           = "grade"
        
class SingleChoiceQustion( Question ):
    """
        Question with single answer
    """
    answers = models.ManyToManyField( Answer, 
                                      verbose_name = "odpowiedzi" )
    
    class Meta:
        verbose_name        = "pytanie jednokrotnego wyboru"
        verbose_name_plural = "pytania jednokrotnego wyboru"
        app_label           = "grade"
        
class MultipleChoiceQuestion( Question ):
    """
        Question with multiple answers
    """
    answers = models.ManyToManyField( Answer, 
                                      verbose_name = "odpowiedzi" )
    
    class Meta:
        verbose_name        = "pytanie wielokrotnego wyboru"
        verbose_name_plural = "pytania wielokrotnego wyboru"
        app_label           = "grade"
