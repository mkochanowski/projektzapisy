# -*- coding: utf-8 -*-

"""
    System State for vote
    Default values are dafined as module variables
"""

from django.db import models
from datetime  import date

DEFAULT_YEAR       = date.today().year 
DEFAULT_MAX_POINTS = 3
DEFAULT_MAX_VOTE   = 30
DEFAULT_DAY_BEG    = 1          #
DEFAULT_DAY_END    = 31         # Te dane trzeba będzie tak ustawić
DEFAULT_MONTH_BEG  = 1          # żeby były prawdziwe. Na razie tak
DEFAULT_MONTH_END  = 12         # jest wygodnie, chociażby do testów
DEFAULT_VOTE_BEG   = date(DEFAULT_YEAR, DEFAULT_MONTH_BEG, DEFAULT_DAY_BEG)
DEFAULT_VOTE_END   = date(DEFAULT_YEAR, DEFAULT_MONTH_END, DEFAULT_DAY_END)

class SystemState( models.Model ):
    """
        System state for vote
    """
    year      = models.IntegerField(
                    verbose_name = 'Rok akademicki',
                    unique       = True,
                    default      = date.today.year())

    max_points = models.IntegerField( 
                    verbose_name = 'Maksimum punktów na przedmiot',
                    default      = DEFAULT_MAX_POINTS )
                    
    max_vote   = models.IntegerField(
                    verbose_name = 'Maksymalna wartość głosu',
                    default      =  DEFAULT_MAX_VOTE)
                    
    vote_beg   = models.DateField(
                    verbose_name = 'Początek głosowania',
                    default      = DEFAULT_VOTE_BEG )
    
    vote_end   = models.DateField(
                    verbose_name = 'Koniec głosowania',
                    default      = DEFAULT_VOTE_END)
                    
    class Meta:
        verbose_name        = 'ustawienia głosowania'
        verbose_name_plural = 'ustawienia głosowań'
        app_label           = 'vote'
        
    def __unicode__( self ):
        return "Ustawienia systemu na rok " + str(self.year)
    
    @staticmethod
    def get_state(year = None):
        """
            Gets actual system state from database
            Creates one if necessary
        """
        if not year:
            year = date.today().year
        try:
            return SystemState.objects.filter(year=year)[0]
        except IndexError:
            return SystemState.create_default_state(year)
    
    @staticmethod
    def create_default_state(year = None):
        """
            Creates system state from default variables
        """
        if not year:
            year = date.today().year
        new_state = SystemState()
        new_state.year      = year
        new_state.max_points = DEFAULT_MAX_POINTS
        new_state.max_vote   = DEFAULT_MAX_VOTE
        new_state.vote_beg   = date(year, DEFAULT_MONTH_BEG, DEFAULT_DAY_BEG)
        new_state.vote_end   = date(year, DEFAULT_MONTH_END, DEFAULT_DAY_END)
        new_state.save()
        return new_state
        
    @staticmethod
    def get_max_points(year = None):
        """
            Get max points per subject
        """
        state = SystemState.get_state(year)
        return state.max_points
        
    @staticmethod
    def get_max_vote(year = None):
        """
            Get max vote value
        """
        state = SystemState.get_state(year)
        return state.max_vote
        
    
    @staticmethod
    def get_vote_beg(year = None):
        """
            Get vote beggining date
        """
        state = SystemState.get_state(year)
        return state.vote_beg
        
    @staticmethod
    def get_vote_end(year = None):
        """
            Get vote ending date
        """
        state = SystemState.get_state(year)
        return state.vote_end
        
    @staticmethod
    def is_vote_active():
        """
            Checks if vote is active
        """
        vote_beg = SystemState.get_vote_beg()
        vote_end = SystemState.get_vote_end()
        
        return vote_beg <= date.today() <= vote_end
