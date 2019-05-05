from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    def get_schema(self):
        pass

    def __str__(self):
        if self.group:
            return (
                f"Ankieta dla grupy: {self.group.get_type_display()} "
                + self.group.get_teacher_full_name()
            )
        elif self.course:
            return f"Ankieta dla kursu: {self.course}"
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

    @classmethod
    def edit(cls, new_schema):
        pass


class Submission(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.DO_NOTHING, null=True)
    answers = JSONField(default=dict)
    ticket = models.TextField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @classmethod
    def get_or_create(cls, ticket):
        pass
