from enum import Enum

from django.db import models

from apps.users.models import Employee, Student
from .validators import validate_num_required_votes
from .system_settings import get_num_required_votes

MAX_THESIS_TITLE_LEN = 300


class ThesisKind(Enum):
    masters = 0
    engineers = 1
    bachelors = 2
    bachelors_engineers = 3
    isim = 4


THESIS_KIND_CHOICES = (
    (ThesisKind.masters.value, "mgr"),
    (ThesisKind.engineers.value, "inż"),
    (ThesisKind.bachelors.value, "lic"),
    (ThesisKind.bachelors_engineers.value, "lic+inż"),
    (ThesisKind.isim.value, "isim"),
)


class ThesisStatus(Enum):
    being_evaluated = 1
    returned_for_corrections = 2
    accepted = 3
    in_progress = 4
    defended = 5
    default = being_evaluated


THESIS_STATUS_CHOICES = (
    (ThesisStatus.being_evaluated.value, "poddana pod głosowanie"),
    (ThesisStatus.returned_for_corrections.value, "zwrócona do poprawek"),
    (ThesisStatus.accepted.value, "zaakceptowana"),
    (ThesisStatus.in_progress.value, "w realizacji"),
    (ThesisStatus.defended.value, "obroniona"),
)


class Thesis(models.Model):
    title = models.CharField(max_length=MAX_THESIS_TITLE_LEN)
    advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True, related_name="thesis_advisor",
    )
    auxiliary_advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True,
        null=True, related_name="thesis_auxiliary_advisor",
    )
    kind = models.SmallIntegerField(choices=THESIS_KIND_CHOICES)
    status = models.SmallIntegerField(choices=THESIS_STATUS_CHOICES)
    reserved = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, blank=True, null=True, related_name="thesis_student",
    )
    student_2 = models.ForeignKey(
        Student, on_delete=models.PROTECT, blank=True, null=True, related_name="thesis_student_2",
    )
    added_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def process_new_votes(self, votes):
        """Whenever one or more votes for a thesis change, this function
        should be called to process & save them
        """
        for voter, vote in votes:
            try:
                existing_vote = ThesisVoteBinding.objects.get(thesis=self, voter=voter)
                existing_vote.value = vote.value
                existing_vote.save()
            except ThesisVoteBinding.DoesNotExist:
                ThesisVoteBinding.objects.create(thesis=self, voter=voter, value=vote.value)
        self.check_for_vote_status_change()

    def check_for_vote_status_change(self):
        """If we have enough approving votes, accept this thesis - unless there's a rejecting
        vote, then we return it for corrections
        """
        approve_votes_cnt = ThesisVoteBinding.objects.filter(
            thesis=self, value=ThesisVote.accepted.value
        ).count()
        reject_votes_cnt = ThesisVoteBinding.objects.filter(
            thesis=self, value=ThesisVote.rejected.value
        ).count()
        if reject_votes_cnt:
            self.status = ThesisStatus.returned_for_corrections.value
        elif approve_votes_cnt >= get_num_required_votes():
            self.status = ThesisStatus.accepted.value
        self.save()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "praca dyplomowa"
        verbose_name_plural = "prace dyplomowe"


class ThesisVote(Enum):
    none = 1
    rejected = 2
    accepted = 3
    user_missing = 4  # not sure about this one


THESIS_VOTE_CHOICES = (
    (ThesisVote.none.value, "brak głosu"),
    (ThesisVote.rejected.value, "odrzucona"),
    (ThesisVote.accepted.value, "zaakceptowana"),
    (ThesisVote.user_missing.value, "brak użytkownika"),
)


def vote_to_string(vote_value):
    for value, vote_string in THESIS_VOTE_CHOICES:
        if value == vote_value:
            return vote_string
    return ""


class ThesisVoteBinding(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name="votes")
    # should be a member of the theses board group
    voter = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="thesis_votes")
    value = models.SmallIntegerField(choices=THESIS_VOTE_CHOICES)

    def __str__(self):
        return f'Głos {self.voter} na {self.thesis} - {vote_to_string(self.value)}'


def filter_ungraded_for_emp(qs, emp: Employee):
    """
    Filter the given queryset to only contain
    all _ungraded_ theses for a given board member.
    A thesis is _ungraded_ if the voter has not cast a vote at all
    or manually set it to none (not possible from the client UI currently)
    Depends on the cusom __ne lookup filter, see apps.py
    """
    # Logic: exclude thesis where there is a vote other than none for the given emp
    # Multiple conditions are ANDed together, see
    # https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.query.QuerySet.exclude
    return qs\
        .exclude(votes__value__ne=ThesisVote.none.value, votes__voter=emp)\
        .distinct()


def get_num_ungraded_for_emp(emp: Employee) -> int:
    """Get the number of ungraded theses for the given employee"""
    ungraded_qs = filter_ungraded_for_emp(Thesis.objects, emp)
    return ungraded_qs.count()


class ThesesSystemSettings(models.Model):
    num_required_votes = models.SmallIntegerField(
        verbose_name="Liczba głosów wymaganych do zaakceptowania",
        validators=[validate_num_required_votes]
    )

    def __str__(self):
        return "Ustawienia systemu"

    class Meta:
        verbose_name = "ustawienia systemu prac dyplomowych"
        verbose_name_plural = "ustawienia systemu prac dyplomowych"
