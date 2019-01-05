from enum import Enum

from django.db import models

from apps.users.models import Employee, Student

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
    title = models.CharField(max_length=MAX_THESIS_TITLE_LEN, unique=True)
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

    def is_archived(self):
        return self.status == ThesisStatus.defended.value

    def __str__(self) -> str:
        return self.title

    def clean(self):
        """Ensure that the title never contains superfluous whitespace"""
        self.title = self.title.strip()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "praca dyplomowa"
        verbose_name_plural = "prace dyplomowe"


class ThesisVote(Enum):
    none = 1
    rejected = 2
    accepted = 3


THESIS_VOTE_CHOICES = (
    (ThesisVote.none.value, "brak głosu"),
    (ThesisVote.rejected.value, "odrzucona"),
    (ThesisVote.accepted.value, "zaakceptowana"),
)


def vote_to_string(vote_value: int) -> str:
    for value, vote_string in THESIS_VOTE_CHOICES:
        if value == vote_value:
            return vote_string
    return ""


class ThesisVoteBinding(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name="votes")
    # should be a member of the theses board group
    voter = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="thesis_votes")
    value = models.SmallIntegerField(choices=THESIS_VOTE_CHOICES)

    def __str__(self) -> str:
        return f'Głos {self.voter} na {self.thesis} - {vote_to_string(self.value)}'


class ThesesSystemSettings(models.Model):
    num_required_votes = models.SmallIntegerField()

    class Meta:
        verbose_name_plural = "ustawienia systemu prac dyplomowych"
