# -*- coding: utf-8 -*-

"""
    Polls
"""

from django.db import models


from fereol.grade.poll.models.question import Question

class Option( models.Model ):
    question    = models.ForeignKey (Question, verbose_name = 'pytanie' )
    title       = models.CharField ( max_length = 250, verbose_name = 'odpowiedz' )

    class Meta:
        verbose_name    = "odpowiedz ankiety"
        verbose_name    = "odpowiedz ankiety"
        app_label       = "poll"

