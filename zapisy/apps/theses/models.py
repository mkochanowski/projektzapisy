from enum import Enum

from django.db import models
from django.db import connection

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
        had_rejection = False
        had_approval = False
        for voter, vote in votes:
            try:
                existing_vote = ThesisVoteBinding.objects.get(thesis=self, voter=voter)
                existing_vote.value = vote.value
                existing_vote.save()
                if vote == ThesisVote.rejected:
                    had_rejection = True
                elif vote == ThesisVote.accepted:
                    had_approval = True
            except ThesisVoteBinding.DoesNotExist:
                ThesisVoteBinding.objects.create(thesis=self, voter=voter, value=vote.value)
        if had_approval:
            self.check_for_approval_status_change()
        elif had_rejection:
            self.status = ThesisStatus.returned_for_corrections.value
            self.save()

    def check_for_approval_status_change(self):
        approve_votes_cnt = ThesisVoteBinding.objects.filter(
            thesis=self, value=ThesisVote.accepted.value
        ).count()
        if approve_votes_cnt >= get_num_required_votes():
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


def get_num_ungraded_for_emp(emp: Employee) -> int:
    """
    Get the number of _ungraded_ theses for a given board member
    A thesis is _ungraded_ if the voter has not cast a vote at all
    or manually set it to none (not possible from the client UI currently)

    Sadly, this uses a handwritten query. The reason is performance:
    this will be called at every normal template render for board members,
    so it must be fast. Timings on an old (Nehalem) i5-750@2.6GHz for 1000 theses,
    on average 4 out of 7 votes each (with all relevant prefetch_related calls):
    1. Pure Django queryset logic: 3.8 sec
    2. Fetch using querysets, then process in Python: 0.8 sec
    3. Manual SQL: 6 msec

    Query explanation: select the number of theses where there are no bindings
    of that thesis and the given member with a vote value other than none (i.e. if
    the given member has cast a non-none vote for this thesis)
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
                select count(*) from theses_thesis t where
                (
                    select count(*) from theses_thesisvotebinding
                    where thesis_id = t.id and value != %s and voter_id = %s
                ) = 0;
            """,
            # Note that there is no risk of injection here, we're passing the parameters
            # as arguments to cursor.execute, not formatting them into the query string
            [ThesisVote.none.value, emp.pk]
        )
        row = cursor.fetchone()
    return row[0]


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
