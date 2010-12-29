# -*- coding: utf-8 -*-

"""
    Generated Polls
"""

from django.db import models


from users.models               import Type
from enrollment.subjects.models import Subject
from enrollment.subjects.models import Group
from grade.poll.models          import Poll
                                               
class GeneratedPoll( models.Model ):
    start             = models.DateTimeField( 
                                    verbose_name = "początek" )
    end               = models.DateTimeField( 
                                    verbose_name = "koniec" )
    description       = models.TextField( verbose_name = "opis" )
    poll              = models.ForeignKey( Poll, verbose_name = "ankieta")
    #
    # Ankieta moze byc przypisana do: grupy, przedmiotu, oraz typu studiow
    # null na danej pozycji oznacza, ze kazdy spelnia kryterium 
    # w szczegolnosci same nulle oznaczaja ankiete dla kazdego
    #
    group             = models.ForeignKey( Group, blank = True,
                                           null = True, verbose_name = "grupa")
    subject           = models.ForeignKey( Subject, blank = True,
                                           null = True, verbose_name = "przedmiot")
    users_group       = models.ForeignKey( Type, blank = True, null = True, verbose_name = "typ studenta")
                         
    class Meta:
        verbose_name        = "Wygenerowana ankieta"
        verbose_name_plural = "Wygenerowane ankiety"
        app_label           = "poll"


