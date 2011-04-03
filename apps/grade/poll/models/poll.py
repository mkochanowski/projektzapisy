# -*- coding: utf-8 -*-

"""
    Polls
"""

from django.db import models

from apps.grade.poll.models.questions import OpenQuestion
from apps.grade.poll.models.questions import SingleChoiceQuestion
from apps.grade.poll.models.questions import MultipleChoiceQuestion

from apps.users.models               import Employee
from apps.enrollment.subjects.models import Subject
from apps.enrollment.subjects.models import Group
                                               
class Poll( models.Model ):
    title   = models.CharField(  max_length   = 250,
                                 verbose_name = "tytuł" )
    author  = models.ForeignKey( Employee,
                                 verbose_name = "autor" )
    subject = models.ForeignKey( Subject,
                                 verbose_name = "przedmiot" )
    group   = models.ForeignKey( Group,
                                 verbose_name = "grupa" )
    
    single_choice_questions = models.ManyToManyField( 
                          SingleChoiceQuestion,
                          blank=True,
                          verbose_name = "pytania jednokrotnego wyboru")
    multiple_choice_question = models.ManyToManyField(
                          MultipleChoiceQuestion,
                          blank=True,
                          verbose_name = "pytania wielokrotnego wyboru")
    open_questions           = models.ManyToManyField(
                          OpenQuestion,
                          blank=True,
                          verbose_name = "pytania otwarte")
                          
    class Meta:
        verbose_name        = "ankieta"
        verbose_name_plural = "ankiety"
        app_label           = "poll"
