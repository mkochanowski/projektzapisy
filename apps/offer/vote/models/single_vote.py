# -*- coding: utf-8 -*-

"""
    Single vote
"""

from datetime  import date
from django.db import models
from django.db.models.aggregates import Sum

from apps.offer.proposal.models          import Proposal
from apps.offer.vote.models.system_state import SystemState

class SingleVote ( models.Model ):
    """
        Student's single vote
    """
    votes = [(0,'0'), (1,'1'), (2, '2'), (3, '3')]

    student = models.ForeignKey('users.Student',
                                verbose_name='głosujący')

    course = models.ForeignKey(Proposal,
                               verbose_name='przedmiot')

    state = models.ForeignKey('vote.SystemState',
                              verbose_name='ustawienia głosowania')

    value = models.IntegerField(choices=votes, default=0, verbose_name='punkty')

    correction = models.IntegerField(choices=votes, default=0, verbose_name='korekta')

    	
    class Meta:
        verbose_name        = 'pojedynczy głos'
        verbose_name_plural = 'pojedyncze głosy'
        app_label           = 'vote'
        ordering            = ('student', '-value', 'course')
        
        unique_together = ('course', 'state', 'student')
        
    def __unicode__( self ):
        return  '[' + str(self.state.year) + u']Głos użytkownika: ' + \
				self.student.user.username + '; ' + self.course.name + \
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
        votes = SingleVote.objects.filter( course = proposal, state=current_state )
        value = 0
        voters = votes.count()
        for vote in votes:
            value += vote.correction

        return value, voters

    @staticmethod
    def get_voters( proposal, year=None ):
        """
            Gets users who voted for specified proposal
        """
        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)
        votes = SingleVote.objects.filter( course = proposal, state=current_state )

        voters = []
        for vote in votes:
            voters.append({'user': vote.student.user, 'points': vote.correction })
        return voters



    @staticmethod
    def get_points_for_student( student, year=None):
        if not year:
            year = date.today().year
        pass

    @staticmethod
    def make_votes( student, year=None ):
        """
            Makes 'zero' vote for student - only for proposal without
            vote
        """
        from apps.offer.proposal.models.proposal import Proposal

        if not year:
            year = date.today().year

        proposals = Proposal.get_by_tag('offer')
        current_state = SystemState.get_state(year)

        old_votes = SingleVote.objects.\
                        filter(student=student, state=current_state).\
                        values_list('course__id', flat=True).order_by('course__id')

        new_votes = []
        for proposal in proposals:
            if proposal.id not in old_votes:
                new_votes.append(proposal)

        for proposal in new_votes:
            vote = SingleVote(student=student,
                               course=proposal,
                               state=current_state,
                               value=0)
            vote.save()


    @staticmethod
    def get_votes_for_proposal( voter, proposals, year=None ):
        """
            Gets user votes in specified year for proposal set
        """
        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)
        votes         = SingleVote.objects.filter(student=voter, course__in=proposals, state=current_state)
        return votes


    @staticmethod
    def sum_votes( student, state ):
        return SingleVote.objects.filter(student=student, state=state).aggregate(votes=Sum('value'))