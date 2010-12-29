# -*- coding: utf-8 -*-

"""
    Polls
"""

from django.db import models
from fereol.grade.poll.models.section import Section, Poll
from fereol.grade.poll.models.poll import Poll

class Question( models.Model ):
    section     = models.ForeignKey( Section, verbose_name = 'sekcja' )
    poll        = models.ForeignKey( Poll, verbose_name = 'ankieta' )
    title       = models.CharField(  max_length   = 250,
                                 verbose_name = "tytuł" )
    type        = models.CharField(  max_length   = 250,
                                 verbose_name = "typ" )
    description = models.CharField(  max_length   = 250,
                                 verbose_name = "opis" )

    class Meta:
        verbose_name        = "pytanie ankiety"
        verbose_name_plural = "pytania ankiety"
        app_label           = "poll"


