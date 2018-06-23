from enum import Enum

from django.db import models

from apps.users.models import Employee, Student


MAX_THESIS_TITLE_LEN = 300

class ThesisKind(Enum):
	masters = 0
	engineers = 1
	bachelors = 2
	bachelors_engineers = 3,
	isim = 4
THESIS_KIND_CHOICES = (
	(ThesisKind.masters, "mgr"),
	(ThesisKind.engineers, "inż"),
	(ThesisKind.bachelors, "lic"),
	(ThesisKind.bachelors_engineers, "lic+inż"),
	(ThesisKind.isim, "isim"),
)

class ThesisStatus(Enum):
	being_evaluated = 1,
	returned_for_corrections = 2,
	accepted = 3,
	in_progress = 4,
	defended = 5,
THESIS_STATUS_CHOICES = (
	(ThesisStatus.being_evaluated, "poddana pod głosowanie"),	
	(ThesisStatus.returned_for_corrections, "zwrócona do poprawek"),
	(ThesisStatus.accepted, "zaakceptowana"),
	(ThesisStatus.in_progress, "w realizacji"),
	(ThesisStatus.defended, "obroniona"),	
)

class Thesis(models.Model):
	title = models.CharField(max_length=MAX_THESIS_TITLE_LEN)
	advisor = models.ForeignKey(
		Employee, on_delete=models.PROTECT, null=True, related_name="thesis_advisor",
	)
	auxiliary_advisor = models.ForeignKey(
		Employee, on_delete=models.PROTECT, null=True, related_name="thesis_auxiliary_advisor",
	)
	kind = models.SmallIntegerField(choices=THESIS_KIND_CHOICES)
	reserved = models.BooleanField(default=False)
	student = models.ForeignKey(
		Student, on_delete=models.PROTECT, null=True, related_name="thesis_student",
	)
	student_2 = models.ForeignKey(
		Student, on_delete=models.PROTECT, null=True, related_name="thesis_student_2",
	)
	added_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="praca dyplomowa"
		verbose_name_plural="prace dyplomowe"

class ThesesCommissionMember(models.Model):
	member = models.ForeignKey(Employee)

	class Meta:
		verbose_name="członek komisji"
		verbose_name_plural="członkowie komisji"


class ThesisVote(Enum):
	none = 1
	rejected = 2
	accepted = 3
	user_missing = 4  # not sure about this one
THESIS_VOTE_CHOICES = (
	(ThesisVote.none, "brak głosu"),
	(ThesisVote.rejected, "odrzucona"),
	(ThesisVote.accepted, "zaakceptowana"),
	(ThesisVote.user_missing, "brak użytkownika"),
)

class ThesisVoteBinding(models.Model):
	thesis = models.ForeignKey(Thesis)
	voter = models.ForeignKey(Employee)  # should be a member of the theses commission
	vote = models.SmallIntegerField(choices=THESIS_VOTE_CHOICES)


class ThesesSystemSettings(models.Model):
	num_required_votes = models.IntegerField()

	class Meta:
		verbose_name_plural="ustawienia systemu prac dyplomowych"
