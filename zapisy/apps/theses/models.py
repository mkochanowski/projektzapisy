from typing import Tuple, NamedTuple, Iterable
from datetime import datetime

from choicesenum import ChoicesEnum
from choicesenum.django.fields import EnumIntegerField
from django.db import models
from django.db.models.expressions import RawSQL

from apps.users.models import Employee, Student, BaseUser
from .validators import validate_num_required_votes, validate_master_rejecter
from .system_settings import get_num_required_votes
from .users import is_admin
from .notifications import (
    notify_thesis_accepted, notify_thesis_rejected,
    notify_rejecting_vote_cast
)

MAX_THESIS_TITLE_LEN = 300
MIN_REJECTION_REASON_LENGTH = 100
MAX_REJECTION_REASON_LENGTH = 500


class ThesisKind(ChoicesEnum):
    MASTERS = 0, "mgr"
    ENGINEERS = 1, "inż"
    BACHELORS = 2, "lic"
    ISIM = 3, "isim"
    # Certain theses will be appropriate for both bachelor and engineer degrees
    BACHELORS_ENGINEERS = 4, "lic+inż"
    BACHELORS_ENGINEERS_ISIM = 5, "lic+inż+isim"


class ThesisStatus(ChoicesEnum):
    BEING_EVALUATED = 1, "weryfikowana przez komisję"
    RETURNED_FOR_CORRECTIONS = 2, "zwrócona do poprawek"
    ACCEPTED = 3, "zaakceptowana"
    IN_PROGRESS = 4, "w realizacji"
    DEFENDED = 5, "obroniona"


class ThesisVote(ChoicesEnum):
    NONE = 1, "brak głosu"
    REJECTED = 2, "odrzucona"
    ACCEPTED = 3, "zaakceptowana"


class VoteToProcess(NamedTuple):
    voter: Employee
    value: ThesisVote
    # if rejecting
    reason: str


VotesToProcess = Iterable[VoteToProcess]


"""Voting for a thesis in one of these statuses is not permitted
for regular board members
"""
UNVOTEABLE_STATUSES = (
    ThesisStatus.ACCEPTED,
    ThesisStatus.IN_PROGRESS,
    ThesisStatus.DEFENDED
)


class Thesis(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Save the status so that, when saving, we can determine whether or not it changed
        # See https://stackoverflow.com/a/1793323
        # If pk is None, we are creating this model, so don't save the status
        self.__original_status = self.status if self.pk is not None else None

    title = models.CharField(max_length=MAX_THESIS_TITLE_LEN, unique=True)
    advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True, related_name="thesis_advisor",
    )
    auxiliary_advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True,
        null=True, related_name="thesis_auxiliary_advisor",
    )
    kind = EnumIntegerField(enum=ThesisKind, default=ThesisKind.MASTERS)
    status = EnumIntegerField(enum=ThesisStatus, default=ThesisStatus.BEING_EVALUATED)
    reserved_until = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, blank=True, null=True, related_name="thesis_student",
    )
    student_2 = models.ForeignKey(
        Student, on_delete=models.PROTECT, blank=True, null=True, related_name="thesis_student_2",
    )
    added = models.DateTimeField(auto_now_add=True)
    # A thesis is _modified_ when its status changes
    modified = models.DateTimeField(auto_now_add=True)
    # The "official" rejection reason, filled out by the rejecter
    rejection_reason = models.TextField(blank=True)

    def on_title_changed_by(self, user: BaseUser):
        if self.advisor == user and not is_admin(user):
            self.votes.all().delete()
            self.status = ThesisStatus.BEING_EVALUATED
            self.save()

    def process_new_votes(
        self, votes: VotesToProcess, changing_user: Employee, should_update_status: True
    ):
        """Whenever one or more votes for a thesis change, this function
        should be called to process & save them

        Arguments:

        changing_user -- The user who's causing the change of votes;
        if they're not changing their own vote, thesis status will not be updated
        (based on the assumption that they're simply adjusting the votes of some
        other voters and don't actually want it to count)

        should_update_status -- Whether the status should be updated based on vote
        counts (only if the condition above holds)
        """
        had_vote_as_self = False
        self_rejecting_vote = None
        for vote in votes:
            if vote.voter == changing_user:
                had_vote_as_self = True
                if vote.value == ThesisVote.REJECTED:
                    self_rejecting_vote = vote
            self.votes.update_or_create(
                voter=vote.voter,
                defaults={
                    "value": vote.value.value,
                    "reason": vote.reason if vote.value == ThesisVote.REJECTED else ""
                }
            )
        if had_vote_as_self and should_update_status:
            self.check_for_vote_status_change()
        if self_rejecting_vote:
            notify_rejecting_vote_cast(self, changing_user, self_rejecting_vote.reason)

    def check_for_vote_status_change(self):
        """If we have enough approving votes, accept this thesis
        Only do this if it's still being evaluated; board members can cast
        votes when it's rejected, but that doesn't change anything
        """
        if (
            ThesisStatus(self.status) == ThesisStatus.BEING_EVALUATED and
            self.get_approve_votes_cnt() >= get_num_required_votes()
        ):
            self.status = ThesisStatus.ACCEPTED
            self.save()

    def get_approve_votes_cnt(self):
        return self.votes.filter(value=ThesisVote.ACCEPTED).count()

    def is_archived(self):
        return self.status == ThesisStatus.DEFENDED

    def __str__(self) -> str:
        return self.title

    def clean(self):
        """Ensure that the title never contains superfluous whitespace"""
        self.title = self.title.strip()

    def adjust_status(self):
        """If there is a student and the thesis has been accepted, we automatically
        move it to "in progress"; conversely, if it was in progress but the students
        have been removed, go back to accepted
        """
        current_status = ThesisStatus(self.status)
        if current_status == ThesisStatus.ACCEPTED and (self.student or self.student_2):
            self.status = ThesisStatus.IN_PROGRESS
        elif current_status == ThesisStatus.IN_PROGRESS and not self.student and not self.student_2:
            self.status = ThesisStatus.ACCEPTED

    def notify_on_status_change(self):
        old_status = ThesisStatus(self.__original_status) if self.__original_status else None
        new_status = ThesisStatus(self.status)
        # it could jump straight to in progress if there is a student defined already
        newly_accepted_statuses = (ThesisStatus.ACCEPTED, ThesisStatus.IN_PROGRESS)
        nonaccepted_statuses = (ThesisStatus.BEING_EVALUATED, ThesisStatus.RETURNED_FOR_CORRECTIONS)
        if (new_status in newly_accepted_statuses and old_status in nonaccepted_statuses):
            notify_thesis_accepted(self)
        elif new_status == ThesisStatus.RETURNED_FOR_CORRECTIONS:
            notify_thesis_rejected(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        if not kwargs.pop("skip_status_update", False):
            self.adjust_status()
        if self.status != self.__original_status:
            # If the status changed, update modified date
            self.modified_date = datetime.now()
            # Maybe send notifications
            self.notify_on_status_change()
        super().save(*args, **kwargs)
        self.__original_status = self.status

    class Meta:
        verbose_name = "praca dyplomowa"
        verbose_name_plural = "prace dyplomowe"


def vote_to_string(vote_value: int) -> str:
    for value, vote_string in ThesisVote.choices():
        if value == vote_value:
            return vote_string
    return ""


class ThesisVoteBinding(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name="votes")
    voter = models.ForeignKey(Employee, on_delete=models.PROTECT)
    value = EnumIntegerField(enum=ThesisVote, default=ThesisVote.NONE)
    # Usually only filled out if the value is 'rejected'
    reason = models.CharField(max_length=MAX_REJECTION_REASON_LENGTH, blank=True)

    def __str__(self) -> str:
        return f'Głos {self.voter} na {self.thesis} - {vote_to_string(self.value)}'


def filter_ungraded_for_emp(qs, emp: Employee):
    """
    Filter the given queryset to only contain
    all _ungraded_ theses for a given board member.
    A thesis is _ungraded_ if the voter has not cast a vote at all
    or manually set it to none (not possible from the client UI currently)
    """
    # Uses custom SQL - I couldn't get querysets to do what I wanted them to;
    # doing .exclude(votes__value__ne=none, votes__voter=emp) doesn't do what you want,
    # it ands two selects together rather than and two conditions in one select
    return qs.filter(
        # While voting for rejected theses is allowed, they're not "priority",
        # so we don't count them here
        status=ThesisStatus.BEING_EVALUATED
    ).annotate(definite_votes=RawSQL(
        """
        select count(*) from theses_thesisvotebinding where
        thesis_id=theses_thesis.id and voter_id=%s and value<>%s
        """,
        (emp.pk, ThesisVote.NONE.value)
    )).filter(definite_votes=0)


def get_num_ungraded_for_emp(emp: Employee) -> int:
    """Get the number of ungraded theses for the given employee"""
    ungraded_qs = filter_ungraded_for_emp(Thesis.objects, emp)
    return ungraded_qs.count()


class ThesesSystemSettings(models.Model):
    num_required_votes = models.SmallIntegerField(
        verbose_name="Liczba głosów wymaganych do zaakceptowania",
        validators=[validate_num_required_votes]
    )
    master_rejecter = models.ForeignKey(
        Employee, null=True, on_delete=models.PROTECT,
        verbose_name="Członek komisji odpowiedzialny za zwracanie prac do poprawek",
        validators=[validate_master_rejecter]
    )

    def __str__(self):
        return "Ustawienia systemu"

    class Meta:
        verbose_name = "ustawienia systemu prac dyplomowych"
        verbose_name_plural = "ustawienia systemu prac dyplomowych"
