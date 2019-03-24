"""
    Single vote
"""

from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, DatabaseError, transaction
from django.db.models.aggregates import Sum
from apps.enrollment.courses.models.course import CourseEntity, Course
from apps.enrollment.courses.models.semester import Semester
from apps.offer.vote.models.system_state import SystemState


class SingleVote (models.Model):
    """
        Student's single vote
    """
    votes = [(0, '0'), (1, '1'), (2, '2'), (3, '3')]

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, verbose_name='głosujący')

    entity = models.ForeignKey(CourseEntity, verbose_name='podstawa', on_delete=models.CASCADE)

    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)

    state = models.ForeignKey(
        'vote.SystemState',
        on_delete=models.CASCADE,
        verbose_name='ustawienia głosowania')

    value = models.IntegerField(choices=votes, default=0, verbose_name='punkty')
    correction = models.IntegerField(choices=votes, default=0, verbose_name='korekta')

    free_vote = models.BooleanField(default=False, verbose_name='Głos nie liczy się do limitu')
    # powyższe pole służy do odróżnienia np glosow dopisanych, ktorych nie chcemy liczyc do limitu

    class Meta:
        verbose_name = 'pojedynczy głos'
        verbose_name_plural = 'pojedyncze głosy'
        app_label = 'vote'
        ordering = ('student', 'entity', '-value')

        unique_together = ('course', 'state', 'student')

    def __str__(self):
        return '[' + str(self.state.year) + ']Głos użytkownika: ' + \
            self.student.user.username + '; ' + self.entity.name + \
            '; ' + str(self.value)

    @staticmethod
    def clean_votes():
        votes = SingleVote.objects.all()
        a = {}
        for v in votes:
            if str(v.student_id) in a:
                if str(v.entity_id) in a[str(v.student_id)]:
                    a[str(v.student_id)][str(v.entity_id)].value = max(
                        a[str(v.student_id)][str(v.entity_id)].value, v.value)
                    a[str(v.student_id)][str(v.entity_id)].save()
                    v.delete()
                else:
                    a[str(v.student_id)][str(v.entity_id)] = v

            if str(v.student_id) not in a:
                a[str(v.student_id)] = {}

    @staticmethod
    def get_votes(voter, year=None, state=None,):
        """
            Gets user votes in specified year
        """
        if not state:
            if not year:
                year = date.today().year
            state = SystemState.get_state(year)

        return SingleVote.objects.filter(
            student=voter,
            state=state,
            correction__gte=1) .select_related(
            'student',
            'student__user',
            'entity').order_by(
            'entity__semester',
            'entity__name')

    @staticmethod
    def add_vote_count(proposals, state):
        return proposals.extra(
            select={
                'votes': "COALESCE((SELECT SUM(vote_singlevote.correction) FROM vote_singlevote WHERE vote_singlevote.entity_id = courses_courseentity.id AND vote_singlevote.state_id = %d), 0)" % state.id,
                'voters': "SELECT COUNT(*) FROM vote_singlevote WHERE vote_singlevote.entity_id = courses_courseentity.id AND vote_singlevote.correction > 0 AND vote_singlevote.state_id = %d" % state.id,
            },
        )

    @staticmethod
    def get_points_and_voters(proposal, year=None, state=None):
        """
            Gets proposal points and voters count in specified year
        """
        if not state:
            if not year:
                year = date.today().year
            current_state = SystemState.get_state(year)
        else:
            current_state = state
        votes = SingleVote.objects.filter(entity=proposal, state=current_state, correction__gte=1)\
            .select_related('student', 'student__user', 'entity')

        value = 0
        voters = 0
        for vote in votes:
            value += vote.correction
            voters += 1

        return value, voters, votes

    @staticmethod
    def make_votes(student, year=None, state=None, tag='summer'):
        """
            Makes 'zero' vote for student - only for proposal without
            vote
        """
        correction = state.is_correction_active()

        semester = None
        if tag == 'winter':
            semester = state.semester_winter
        if tag == 'summer':
            semester = state.semester_summer

        year = year if year else date.today().year

        proposals = CourseEntity.objects.filter(status=CourseEntity.STATUS_TO_VOTE, deleted=False)
        current_state = SystemState.get_state(year)

        old_votes = SingleVote.objects.\
            filter(student=student, state=current_state).\
            values_list('entity__id', flat=True).order_by('entity__id')

        new_votes = []
        for proposal in proposals:
            if proposal.id not in old_votes:
                kwargs = {'student': student, 'entity': proposal, 'state': current_state}
                if correction:
                    try:
                        kwargs['course'] = Course.objects.get(semester=semester, entity=proposal)
                    except ObjectDoesNotExist:
                        pass
                new_votes.append(SingleVote(**kwargs))

        if new_votes:
            SingleVote.objects.bulk_create(new_votes)

    @staticmethod
    def get_votes_for_proposal(voter, proposals, year=None):
        #        """
        #            Gets user votes in specified year for proposal set
        #        """
        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)

        return SingleVote.objects.filter(student=voter, state=current_state, entity__in=proposals)\
            .select_related('entity',
                            'entity__owner',
                            'entity__owner__user',
                            'entity__type')

    @staticmethod
    def sum_votes(student, state):
        return SingleVote.objects.filter(
            student=student,
            state=state,
            entity__type__free_in_vote=False).aggregate(
            votes=Sum('value'))

    @staticmethod
    def sum_old_votes(student, state):
        return SingleVote.objects.filter(
            student=student,
            state=state,
            entity__type__free_in_vote=False) .extra(
            where=[
                '(SELECT COUNT(*) FROM courses_course cc WHERE cc.entity_id = vote_singlevote.entity_id AND cc.semester_id = ' +
                str(
                    state.semester_summer_id) +
                ') = 0']) .aggregate(
            votes=Sum('correction'))

    @staticmethod
    def limit_in_summer_correction(student, state):
        all = SingleVote.objects.filter(
            student=student, state=state, entity__type__free_in_vote=False) .extra(
            where=["vote_singlevote.entity_id IN (SELECT id FROM courses_courseentity WHERE semester = 'l')"]) .aggregate(
            votes=Sum('value'))

        return all['votes']

    @staticmethod
    def limit_in_winter_correction(student, state):
        all = SingleVote.objects.filter(
            student=student, state=state, entity__type__free_in_vote=False) .extra(
            where=["vote_singlevote.entity_id IN (SELECT id FROM courses_courseentity WHERE semester = 'z')"]) .aggregate(
            votes=Sum('value'))

        return all['votes']

    def get_vote(self):
        return self.correction

    @classmethod
    def populate_scheduled_courses(cls, semester: Semester):
        """Populates course filed in all singlevotes for a given semester/year.

        When the schedule for semester is known, Course instances are created in
        the database for CourseEntities. These course instances can be then
        referred to in SingleVote object course field. This will make data more
        consistent and opening times easier to compute.
        """
        with transaction.atomic():
            cls.objects.filter(value=0, correction=0).delete()
            course: Course
            for course in Course.objects.filter(semester=semester):
                cls.objects.filter(
                    models.Q(state__semester_winter_id=semester.id) |
                    models.Q(state__semester_summer_id=semester.id),
                    entity_id=course.entity_id,
                    course__isnull=True
                ).update(course=course)
