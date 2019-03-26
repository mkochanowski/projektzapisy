from datetime import datetime

from choicesenum import ChoicesEnum
from choicesenum.django.fields import EnumIntegerField
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
            self.modified = datetime.now()
        super().save(*args, **kwargs)
        self.__original_status = self.status

    class Meta:
        verbose_name = "praca dyplomowa"
        verbose_name_plural = "prace dyplomowe"
