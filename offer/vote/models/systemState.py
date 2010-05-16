# -*- coding: utf-8 -*-

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
     
    year      = models.IntegerField(
                    verbose_name = 'Rok akademicki',
                    unique       = True,
                    default      = DEFAULT_YEAR)

    maxPoints = models.IntegerField( 
                    verbose_name = 'Maksimum punktów na przedmiot',
                    default      = DEFAULT_MAX_POINTS )
                    
    maxVote   = models.IntegerField(
                    verbose_name = 'Maksymalna wartość głosu',
                    default      =  DEFAULT_MAX_VOTE)
                    
    voteBeg   = models.DateField(
                    verbose_name = 'Początek głosowania',
                    default      = DEFAULT_VOTE_BEG )
    
    voteEnd   = models.DateField(
                    verbose_name = 'Koniec głosowania',
                    default      = DEFAULT_VOTE_END)
                    
    class Meta:
        verbose_name        = 'ustawienia głosowania'
        verbose_name_plural = 'ustawienia głosowań'
        app_label           = 'vote'
        
    def __unicode__( self ):
        return "Ustawienia systemu na rok " + str(self.year)
    
    # pobiera aktualny stan systemu    
    @staticmethod
    def get_state(yearC = date.today().year):
        return SystemState.objects.filter(year=yearC)
    
    # tworzy stan systemu o wartościach domyślnych
    @staticmethod
    def create_default_state(year = date.today().year):
        newState = SystemState()
        newState.year      = year
        newState.maxPoints = DEFAULT_MAX_POINTS
        newState.maxVote   = DEFAULT_MAX_VOTE
        newState.voteBeg   = date(year, DEFAULT_MONTH_BEG, DEFAULT_DAY_BEG)
        newState.voteEnd   = date(year, DEFAULT_MONTH_END, DEFAULT_DAY_END)
        newState.save()
        
    # poniższe funkcje służa do uzyskania odpowiednich danych ze stanu
    # systemu na podany rok. Jeśli stan nie istenieje to zostanie 
    # automatycznie utworzony
    @staticmethod
    def get_maxPoints(year = date.today().year):
        state = SystemState.get_state(year)
        
        try:
            return state[0].maxPoints
        except IndexError:
            SystemState.create_default_state(year)
            return DEFAULT_MAX_POINTS
        
    @staticmethod
    def get_maxVote(year = date.today().year):
        state = SystemState.get_state(year)
        
        try:
            return state[0].maxVote
        except IndexError:
            SystemState.create_default_state(year)
            return DEFAULT_MAX_VOTE
    
    @staticmethod
    def get_voteBeg(year = date.today().year):
        state = SystemState.get_state(year)
        
        try:
            return state[0].voteBeg
        except IndexError:
            SystemState.create_default_state(year)
            return date(year, DEFAULT_MONTH_BEG, DEFAULT_DAY_BEG)
        
    @staticmethod
    def get_voteEnd(year = date.today().year):
        state = SystemState.get_state(year)
        
        try:
            return state[0].voteEnd
        except IndexError:
            SystemState.create_default_state(year)
            return date(year, DEFAULT_MONTH_END, DEFAULT_DAY_END)
    
    # sprawdza czy głosowanie jest aktywne
    @staticmethod
    def is_vote_active():
        voteBeg = SystemState.get_voteBeg()
        voteEnd = SystemState.get_voteEnd()
        
        return voteBeg <= date.today() <= voteEnd
