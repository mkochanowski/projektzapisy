# -*- coding: utf-8 -*-

"""
    Single vote
"""

from datetime  import date
from django.db import models
from django.db.models.aggregates import Sum
from apps.enrollment.courses.models.course import CourseEntity, Course

from apps.offer.proposal.models          import Proposal
from apps.offer.vote.models.system_state import SystemState

class SingleVote ( models.Model ):
    """
        Student's single vote
    """
    votes = [(0,'0'), (1,'1'), (2, '2'), (3, '3')]

    student = models.ForeignKey('users.Student',
                                verbose_name='głosujący')

    entity = models.ForeignKey(CourseEntity, verbose_name='podstawa')

    course   = models.ForeignKey(Course, null=True, blank=True)


    state = models.ForeignKey('vote.SystemState',
                              verbose_name='ustawienia głosowania')

    value      = models.IntegerField(choices=votes, default=0, verbose_name='punkty')
    correction = models.IntegerField(choices=votes, default=0, verbose_name='korekta')

    	
    class Meta:
        verbose_name        = 'pojedynczy głos'
        verbose_name_plural = 'pojedyncze głosy'
        app_label           = 'vote'
        ordering            = ('student', 'entity', '-value' )
        
        unique_together = ('course', 'state', 'student')
        
    def __unicode__( self ):
        return  '[' + str(self.state.year) + u']Głos użytkownika: ' + \
				self.student.user.username + '; ' + self.entity.name + \
				'; ' + str(self.value)

    @staticmethod
    def clean_votes():
        votes = SingleVote.objects.all()
        a = {}
        for v in votes:
            if str(v.student_id) in a:
                if str(v.entity_id) in a[str(v.student_id)]:
                    a[str(v.student_id)][str(v.entity_id)].value = max(a[str(v.student_id)][str(v.entity_id)].value, v.value )
                    a[str(v.student_id)][str(v.entity_id)].save()
                    v.delete()
                else:
                    a[str(v.student_id)][str(v.entity_id)] = v

            if str(v.student_id) not in a:
                a[str(v.student_id)] = {}

    @staticmethod
    def connect_with_courses(state, tag):
        if tag == 'summer':
            semester = state.semester_summer

        elif tag == 'winter':
            semester = state.semester_winter

        else:
            return

        for c in Course.objects.filter(semester=semester):
            if c.entity:
                SingleVote.objects.filter(state=state, entity=c.entity).update(course=c)



    @staticmethod
    def get_votes( voter, year=None ):
        """
            Gets user votes in specified year
        """
        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)
        votes = SingleVote.objects.filter( student=voter, state=current_state,correction__gte=1)\
                                  .select_related('student','student__user', 'entity')
        return votes

    @staticmethod
    def get_points_and_voters( proposal, year=None, state=None ):
        """
            Gets proposal points and voters count in specified year
        """
        if not state:
            if not year:
                year = date.today().year
            current_state = SystemState.get_state(year)
        else:
            current_state = state
        votes = SingleVote.objects.filter( entity = proposal, state=current_state, correction__gte=1 )\
                    .select_related('student','student__user', 'entity')
        value = 0
        voters = 0
        for vote in votes:
            value += vote.correction
            voters += 1

        return value, voters, votes

    @staticmethod
    def get_voters( proposal, year=None ):
        """
            Gets users who voted for specified proposal
        """
        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)
        votes = SingleVote.objects.filter( votes__gte=1, entity = proposal, state=current_state ).select_related('student', 'student__user')

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


        year = year if year else date.today().year

        proposals     = CourseEntity.objects.filter(status=2, deleted=False)
        current_state = SystemState.get_state(year)

        old_votes = SingleVote.objects.\
                        filter(student=student, state=current_state).\
                        values_list('entity__id', flat=True).order_by('entity__id')

        new_votes = []
        for proposal in proposals:
            if proposal.id not in old_votes:
                new_votes.append(SingleVote(student=student,
                                               entity=proposal,
                                               state=current_state))

        if new_votes:
            SingleVote.objects.bulk_create(new_votes)



    @staticmethod
    def get_votes_for_proposal( voter, proposals, year=None ):
#        """
#            Gets user votes in specified year for proposal set
#        """
        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)

        return SingleVote.objects.filter(student=voter, entity__in=proposals, state=current_state)\
                    .select_related('entity',
                                    'entity__owner',
                                    'entity__owner__user',
                                    'entity__type')

    @staticmethod
    def get_votes_in_semester( voter, state, tag ):
#        """
#            Gets user votes in specified year for proposal set
#        """
        if tag == 'summer':
            semester = state.semester_summer

        elif tag == 'winter':
            semester = state.semester_winter

        return SingleVote.objects.filter(student=voter, entity__courses__semester=semester)\
                    .select_related('entity',
                                    'entity__owner',
                                    'entity__owner__user',
                                    'entity__type')



    @staticmethod
    def sum_votes( student, state ):
        return SingleVote.objects.filter(student=student, state=state).aggregate(votes=Sum('value'))

    @staticmethod
    def sum_votes( student, state ):
        return SingleVote.objects.filter(student=student, state=state).aggregate(votes=Sum('value'))


    def get_vote(self):
        return self.correction
