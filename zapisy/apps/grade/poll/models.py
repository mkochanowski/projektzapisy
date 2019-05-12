from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.enrollment.courses.models.course import Course
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records import models as records_models
from apps.users.models import Student
from apps.grade.poll.enums import PollType


class Poll(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "ankieta"
        verbose_name_plural = "ankiety"

    @property
    def type(self):
        if self.group == None and self.course == None:
            return PollType.GENERAL
        if self.semester == None and self.group == None:
            return PollType.EXAM
        return self.group.type

    def __str__(self):
        if self.group:
            group_type = self.group.get_type_display().capitalize()
            teacher_name = self.group.get_teacher_full_name()

            return f"{group_type}: {teacher_name}"
        elif self.course:
            return f"Egzamin: {self.course.owner}"
        elif self.semester:
            return f"Semestr {self.semester}"

        return "Ankieta ogólna"

    @property
    def category(self) -> str:
        if self.course:
            return self.course.name
        elif self.group:
            return self.group.course.name
        else:
            return "Ankiety ogólne"

    @property
    def subcategory(self) -> str:
        return self

    def serialize_for_signing_protocol(self):
        result = {}

        if self.group:
            result["name"] = self.group.course.name
            result["type"] = self.group.get_type_display()
        if self.course:
            result["name"] = self.course.name
            result["type"] = "egzamin"
        if self.semester:
            result["name"] = self.semester.get_name()
            result["type"] = "ankieta ogólna"

        result["id"] = self.pk

        return result

    def is_student_entitled_to_poll(self, student: Student):
        """Checks if the student should be able to participate in the poll."""
        if self.group:
            if not records_models.Record.is_enrolled(student.id, self.group_id):
                return False
        # TODO: if self.course
        return True

    @staticmethod
    def get_all_polls_for_student(student: Student) -> list:
        polls = []
        current_semester = Semester.get_current_semester()
        poll_for_semester = Poll.objects.filter(semester=current_semester).first()
        if poll_for_semester:
            polls.append(poll_for_semester)

        records = records_models.Record.objects.filter(
            student=student, status=records_models.RecordStatus.ENROLLED
        ).select_related("group")

        for record in records:
            group = record.group
            course = group.course
            semester = course.semester

            if semester == current_semester:
                if course.exam:
                    poll_for_course = Poll.objects.filter(course=course).first()
                    if poll_for_course and poll_for_course not in polls:
                        polls.append(poll_for_course)

                poll_for_group = Poll.objects.filter(group=group).first()
                if poll_for_group:
                    polls.append(poll_for_group)

        return polls


class Schema(models.Model):
    questions = JSONField(default=dict)
    type = models.CharField(choices=PollType.choices(), max_length=80)

    class Meta:
        verbose_name = "szablon"
        verbose_name_plural = "szablony"

    @classmethod
    def edit(cls, new_schema):
        pass

    @classmethod
    def get_schema_from_file(cls, poll_type):
        return {
            "version": 1,
            "schema": [
                {"question": "To jest testowe pytanie.", "type": "short_open_answer"},
                {
                    "question": "To jest długie otwarte pytanie.",
                    "type": "long_open_answer",
                },
                {
                    "question": "Uważasz, że w stosunku do otrzymanej oceny, Twoje umiejętności są",
                    "type": "predefined_choices_personal_evaluation",
                },
                {
                    "question": "Ile czasu tygodniowo, poza zajęciami, regularnie przeznaczasz na studiowanie? ",
                    "type": "predefined_choices_time_stretched",
                },
                {
                    "question": "Ile średnio czasu tygodniowo poświęcałeś na przygotowanie się do zajęć? ",
                    "type": "predefined_choices_time_short",
                },
                {
                    "question": "Czy egzamin był trudny?",
                    "type": "predefined_choices_grade",
                },
            ],
        }

    @classmethod
    def get_latest(cls, poll_type):
        schema = cls.objects.filter(type=poll_type).first()
        if not schema:
            schema = cls(
                questions=cls.get_schema_from_file(poll_type=poll_type), type=poll_type
            )
            schema.save()

        return schema

    @staticmethod
    def get_default_value_for_question_type(question_type):
        return ""

    def get_schema_with_default_answers(self):
        if (
            self.questions
            and "version" in self.questions
            and "schema" in self.questions
        ):
            schema_with_answers = {
                "version": self.questions["version"],
                "schema": list(
                    map(
                        lambda x: {
                            "question": x["question"],
                            "type": x["type"],
                            "answer": self.get_default_value_for_question_type(
                                x["type"]
                            ),
                        },
                        self.questions["schema"],
                    )
                ),
            }

            return schema_with_answers


class Submission(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.DO_NOTHING, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.DO_NOTHING, null=True)
    answers = JSONField(default=dict)
    ticket = models.TextField(unique=True)
    submitted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "złoszenie"
        verbose_name_plural = "zgłoszenia"

    def __str__(self):
        return str(self.poll)

    @property
    def category(self) -> str:
        if self.poll:
            return self.poll.category

        return "Ankiety ogólne"

    @classmethod
    def get_or_create(cls, poll_with_ticket_id) -> "Submission":
        ticket, poll = poll_with_ticket_id
        submission = cls.objects.filter(ticket=ticket).first()
        if not submission:
            print("Creating new submission")
            schema = Schema.get_latest(poll_type=poll.type)
            answers = schema.get_schema_with_default_answers()
            print(f"schema={schema}, answers={answers}")
            submission = cls(schema=schema, answers=answers, ticket=ticket, poll=poll)
            submission.save()

        return submission
