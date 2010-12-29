# -*- coding: utf-8 -*-

"""
    Polls
"""

from django.db import models

from fereol.grade.poll.models.poll import Poll


class Section( models.Model ):
    title   = models.CharField(  max_length   = 250,
                                 verbose_name = "tytuł" )
    poll    = models.ForeignKey ( Poll, verbose_name = 'ankieta' )
    
    class Meta:
        verbose_name        = "sekcja ankiety"
        verbose_name_plural = "sekcje ankiety"
        app_label           = "poll"
    
    def __unicode__( self ):
        return unicode( self.title )
