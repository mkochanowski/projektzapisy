from django import forms
from django.contrib import messages
from django.forms import Form, ModelForm

from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.enums import (
    SchemaAttendanceAnswers,
    SchemaGenericAnswers,
    SchemaPersonalEvaluationAnswers,
    SchemaTimeLongAnswers,
    SchemaTimeMediumAnswers,
    SchemaTimeShortAnswers,
)
from apps.grade.poll.models import Submission
from apps.grade.poll.utils import check_grade_status


class TicketsEntryForm(forms.Form):
    """A form used for inserting tickets."""
    tickets = forms.CharField(widget=forms.Textarea, label="Klucze do głosowania")


class SubmissionEntryForm(forms.ModelForm):
    """A form responsible for processing submissions for polls.

    The main logic for detecting and parsing the schema for various
    question types is defined in the `__determine_field_by_type()`
    method. Out of the box, this method provides support for textareas
    (for both short and long answers) as well as various types of
    radioselects defined in the `apps.grade.poll.enum` classes.

    The save() method can only process the data when grade is active
    for a semester corresponding to the poll's semester.
    When the grade either is not active or it is active for a different
    semester, all data will be displayed as `readonly` without the
    opportunity to introduce new changes.
    """
    def __init__(self, *args, **kwargs):
        self.jsonfields = kwargs.pop("jsonfields", None)
        super().__init__(*args, **kwargs)
        self.is_grade_active = self.instance.poll.get_semester.is_grade_active
        for index, field in enumerate(self.jsonfields):
            form_field = self.__determine_field_by_type(
                question=field["question"],
                question_type=field["type"],
                active=self.is_grade_active,
            )

            self.fields[f"field_{index}"] = form_field

    def save(self, commit=True):
        """Updates the submission.

        This method performs the actual operation only if the grade
        is active for the poll's semester.
        """
        if self.is_grade_active:
            updated_answers = self.instance.answers
            for index, field in enumerate(self.jsonfields):
                field_name = f"field_{index}"
                updated_answers["schema"][index] = {
                    "question": field["question"],
                    "type": field["type"],
                    "answer": self.cleaned_data.get(field_name),
                }

            self.instance.submitted = True
            self.instance.answers = updated_answers

            return super().save(commit)

    @staticmethod
    def __determine_field_by_type(question: str, question_type: str, active=True):
        """Uses the `question_type` to correctly identify what field
        should be used according to the rules defined in schema.

        :param question: a string that will be used as a label for the field.
        :param question_type: a schema-compatible type of the field.
        :param active: whether the field will be active or disabled.
        :returns: a Django Forms field.
        """
        choices_field_prefix = "predefined_choices"
        if question_type == "long_open_answer":
            form_field = forms.CharField(
                widget=forms.Textarea, label=question, required=False
            )
        elif question_type.startswith(choices_field_prefix):
            question_type = question_type[len(choices_field_prefix):]
            if question_type == "personal_evaluation":
                choices = SchemaPersonalEvaluationAnswers.choices()
            elif question_type == "time_long":
                choices = SchemaTimeLongAnswers.choices()
            elif question_type == "time_medium":
                choices = SchemaTimeMediumAnswers.choices()
            elif question_type == "time_short":
                choices = SchemaTimeShortAnswers.choices()
            elif question_type == "attendance":
                choices = SchemaAttendanceAnswers.choices()
            else:
                choices = SchemaGenericAnswers.choices()

            attrs = {"disabled": "disabled"} if not active else {}
            form_field = forms.ChoiceField(
                choices=choices,
                label=question,
                widget=forms.RadioSelect(choices=choices, attrs=attrs),
                required=True,
            )
        else:
            form_field = forms.CharField(label=question, required=False)

        if not active:
            form_field.widget.attrs["readonly"] = True
        return form_field

    class Meta:
        model = Submission
        fields = []
