# -*- coding: utf-8 -*-

"""
    Polls
"""

from django.db import models

from grade.poll.models.questions import OpenQuestion
from grade.poll.models.questions import SingleChoiceQustion 
from grade.poll.models.questions import MultipleChoiceQuestion

from users.models               import Employee
from enrollment.subjects.models import Subject
from enrollment.subjects.models import Group
                                               
class Poll( models.Model ):
    author  = models.ForeignKey( Employee,
                                 verbose_name = "autor" )
    subject = models.ForeignKey( Subject,
                                 verbose_name = "przedmiot" )
    group   = models.ForeignKey( Group,
                                 verbose_name = "grupa" )
    
    single_choice_questions = models.ManyToManyField( 
                          SingleChoiceQustion,
                          verbose_name = "pytania jednokrotnego wyboru")
    multiple_choice_question = models.ManyToManyField(
                          MultipleChoiceQuestion,
                          verbose_name = "pytania wielokrotnego wyboru")
    open_questions           = models.ManyToManyField(
                          OpenQuestion,
                          verbose_name = "pytania otwarte")
                          
    class Meta:
        verbose_name        = "ankieta"
        verbose_name_plural = "ankiety"
        app_label           = "grade"
