# -*- coding: utf-8 -*-

"""
    Single vote
"""

from datetime  import date
from django.db import models

from offer.proposal.models          import Proposal
from offer.vote.models.system_state import SystemState

class SingleVote ( models.Model ):
    """
        Student's single vote
    """
    student = models.ForeignKey  ( 'users.Student',
                                    verbose_name = 'głosujący' )
                                    
    subject = models.ForeignKey  ( Proposal, 
                                   verbose_name = 'przedmiot')

    state   = models.ForeignKey  ( 'vote.SystemState',
                                   verbose_name = 'ustawienia głosowania')
    
    value   = models.IntegerField( verbose_name = 'punkty')
    	
    class Meta:
        verbose_name        = 'pojedynczy głos'
        verbose_name_plural = 'pojedyncze głosy'
        app_label           = 'vote'
        ordering            = ('student', '-value', 'subject')
        
        unique_together = ('subject', 'state', 'student')
        
    def __unicode__( self ):
        return  '[' + str(self.state.year) + u']Głos użytkownika: ' + \
				self.student.user.username + '; ' + self.subject.name + \
				'; ' + str(self.value)

    @staticmethod
    def get_votes( voter, year=None ):
        """
            Gets user votes in specified year
        """
        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)
        votes = SingleVote.objects.filter( student=voter, state=current_state)
        return votes

    @staticmethod
    def get_points_and_voters( proposal, year=None ):
        """
            Gets proposal points and voters count in specified year
        """
        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)
        votes = SingleVote.objects.filter( subject = proposal, state=current_state )
        value = 0
        voters = votes.count()
        for vote in votes:
            value += vote.value
            
        return value, voters

    @staticmethod
    def get_voters( proposal, year=None ):
        """
            Gets users who voted for specified proposal
        """
        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)
        votes = SingleVote.objects.filter( subject = proposal, state=current_state )
        
        users = []
        for vote in votes:
            users.append(vote.student.user)
        return users
