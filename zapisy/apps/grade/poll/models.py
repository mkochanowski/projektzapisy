from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.shortcuts import reverse

from choicesenum import ChoicesEnum

from apps.enrollment.courses.models.course import Course
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records import models as records_models
from apps.users.models import Student

# Temporary enum
class PollType(ChoicesEnum):
    LECTURE = 1, "ankieta dla wykładu"
    EXERCISE = 2, "ankieta dla ćwiczeń"
    LABS = 3, "ankieta dla pracowni"
    EXERCISE_LABS = 5, "ankieta dla ćwiczenio-pracowni"
    SEMINARY = 6, "ankieta dla seminarium"
    LECTORATE = 7, "ankieta dla lektoratu"
    PHYSICAL_EDUCATION = 8, "ankieta dla zajęć wf"
    REPETITORY = 9, "ankieta dla repetytorium"
    PROJECT = 10, "ankieta dla projektu"
    EXAM = 1000, "ankieta dla egzaminu"
    GENERAL = 1001, "ankieta ogólna"


class Poll(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True)
    # key = models.ForeignKey(SigningKey, on_delete=models.DO_NOTHING)

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
            return (
                f"Ankieta dla grupy: {self.group.get_type_display()} "
                + self.group.get_teacher_full_name()
            )
        elif self.course:
            return f"Ankieta dla przedmiotu: {self.course}"
        elif self.semester:
            return f"Ankieta ogólna: semestr {self.semester}"

        return "Ankieta"

    @staticmethod
    def get_polls_courses_and_general(student: Student) -> (dict, list):
        polls = Poll.get_all_polls_for_student(student)

        courses = {}
        general = []
        for poll in polls:
            if poll.group:
                if poll.group.course_id not in courses:
                    courses[poll.group.course_id] = {
                        "courses": poll.group.course,
                        "polls": [],
                    }
                courses[poll.group.course_id]["polls"].append(poll)
            else:
                general.append(poll)

        return courses, general

    def serialize_for_signing_protocol(self):
        result = {}

        if self.group is None:
            result["type"] = "Ankieta Ogólna"
            result["name"] = "Ankieta Ogólna"
        else:
            result["type"] = self.group.get_type_display()
            result["name"] = self.group.course.name

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
        semester_poll = Poll.objects.filter(semester=current_semester).first()
        if semester_poll:
            polls.append(semester_poll)

        records = records_models.Record.objects.filter(
            student=student, status=records_models.RecordStatus.ENROLLED
        ).select_related("group")

        for record in records:
            group = record.group
            course = group.course
            semester = course.semester

            if semester == current_semester:
                course_poll = Poll.objects.filter(course=course).first()
                if course_poll and course_poll not in polls:
                    polls.append(course_poll)

                group_poll = Poll.objects.filter(group=group).first()
                if group_poll:
                    polls.append(group_poll)

        return polls

    @staticmethod
    def get_all_polls_for_student_as_dict(student: Student) -> dict:
        polls = Poll.get_all_polls_for_student(student)

        return {poll.pk: poll for poll in polls}


class Schema(models.Model):
    questions = JSONField(default=dict)
    # poll = models.ForeignKey(Poll, on_delete=models.DO_NOTHING)
    poll_type = models.CharField(choices=PollType.choices(), max_length=80)

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
        schema = cls.objects.filter(poll_type=poll_type).first()
        if not schema:
            schema = cls(
                questions=cls.get_schema_from_file(poll_type=poll_type),
                poll_type=poll_type,
            )
            schema.save()

        return schema

    @staticmethod
    def get_default_value_for_question_type(question_type):
        return ""

    def get_schema_with_default_answers(self):
        if self.questions and "version" in self.questions and "schema" in self.questions:
            schema_with_answers = {
                "version": self.questions["version"],
                "schema": list(map(
                    lambda x: {
                        "question": x["question"],
                        "type": x["type"],
                        "answer": self.get_default_value_for_question_type(x["type"]),
                    },
                    self.questions["schema"])
                ),
            }

            return schema_with_answers


class Submission(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.DO_NOTHING, null=True)
    answers = JSONField(default=dict)
    ticket = models.TextField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "złoszenie"
        verbose_name_plural = "zgłoszenia"

    @classmethod
    def get_or_create(cls, ticket: int, poll: Poll):
        submission = cls.objects.filter(ticket=ticket).first()
        if not submission:
            print("Creating new submission")
            schema = Schema.get_latest(poll_type=poll.type)
            answers = schema.get_schema_with_default_answers()
            print(f"schema={schema}, answers={answers}")
            submission = cls(schema=schema, answers=answers, ticket=ticket)
            submission.save()

        return submission
