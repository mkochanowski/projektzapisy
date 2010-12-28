# -*- coding: utf-8 -*-

"""
    Polls
"""

from django.db import models


from users.models               import Employee
from enrollment.subjects.models import Subject
from enrollment.subjects.models import Group
                                               
class Poll( models.Model ):
    title   = models.CharField(  max_length   = 250,
                                 verbose_name = "tytuł" )
    author  = models.ForeignKey( Employee,
                                 verbose_name = "autor" )
                         
    class Meta:
        verbose_name        = "ankieta"
        verbose_name_plural = "ankiety"
        app_label           = "poll"

