from enum import Enum
from datetime import datetime

from choicesenum import ChoicesEnum
from django.db import models

from apps.users.models import Employee, Student

MAX_THESIS_TITLE_LEN = 300


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
    DEFAULT = BEING_EVALUATED


class Thesis(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Save the status so that, when saving, we can determine whether or not it changed
        # See https://stackoverflow.com/a/1793323
        self.__original_status = self.status

    title = models.CharField(max_length=MAX_THESIS_TITLE_LEN, unique=True)
    advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True, null=True, related_name="thesis_advisor",
    )
    auxiliary_advisor = models.ForeignKey(
        Employee, on_delete=models.PROTECT, blank=True,
        null=True, related_name="thesis_auxiliary_advisor",
    )
    kind = models.SmallIntegerField(choices=ThesisKind.choices())
    status = models.SmallIntegerField(choices=ThesisStatus.choices())
    reserved_until = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, blank=True, null=True, related_name="thesis_student",
    )
    student_2 = models.ForeignKey(
        Student, on_delete=models.PROTECT, blank=True, null=True, related_name="thesis_student_2",
    )
    added_date = models.DateTimeField(auto_now_add=True)
    # A thesis is _modified_ when its status changes
    modified_date = models.DateTimeField(auto_now_add=True)

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

    def save(self, *args, **kwargs):
        self.full_clean()
        self.adjust_status()
        if self.status != self.__original_status:
            # If the status changed, update modified date
            self.modified_date = datetime.now()
        super().save(*args, **kwargs)
        self.__original_status = self.status

    class Meta:
        verbose_name = "praca dyplomowa"
        verbose_name_plural = "prace dyplomowe"


class ThesisVote(ChoicesEnum):
    NONE = 1, "brak głosu"
    REJECTED = 2, "odrzucona"
    ACCEPTED = 3, "zaakceptowana"


def vote_to_string(vote_value: int) -> str:
    for value, vote_string in ThesisVote.choices():
        if value == vote_value:
            return vote_string
    return ""


class ThesisVoteBinding(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name="votes")
    # should be a member of the theses board group
    voter = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="thesis_votes")
    value = models.SmallIntegerField(choices=ThesisVote.choices())

    def __str__(self) -> str:
        return f'Głos {self.voter} na {self.thesis} - {vote_to_string(self.value)}'


class ThesesSystemSettings(models.Model):
    num_required_votes = models.SmallIntegerField()

    def __str__(self):
        return "Ustawienia systemu"

    class Meta:
        verbose_name = "ustawienia systemu prac dyplomowych"
        verbose_name_plural = "ustawienia systemu prac dyplomowych"
