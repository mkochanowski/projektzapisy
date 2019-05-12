from django.forms import ModelForm, Form
from django import forms

from .models import Submission

from apps.grade.poll.enums import (
    SchemaPersonalEvaluationAnswers,
    SchemaTimeShortAnswers,
    SchemaTimeLongAnswers,
    SchemaGenericAnswers,
)


class TicketsEntryForm(forms.Form):
    tickets = forms.CharField(widget=forms.Textarea, label="Klucze do głosowania")


class SubmissionEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.jsonfields = kwargs.pop("jsonfields", None)
        super().__init__(*args, **kwargs)

        for index, field in enumerate(self.jsonfields):
            if field["type"] == "short_open_answer":
                form_field = forms.CharField(label=field["question"], required=False)
            elif field["type"] == "long_open_answer":
                form_field = forms.CharField(
                    widget=forms.Textarea, label=field["question"], required=False
                )
            elif field["type"].startswith("predefined_choices"):
                if field["type"] == "predefined_choices_personal_evaluation":
                    choices = SchemaPersonalEvaluationAnswers.choices()
                elif field["type"] == "predefined_choices_time_stretched":
                    choices = SchemaTimeLongAnswers.choices()
                elif field["type"] == "predefined_choices_time_short":
                    choices = SchemaTimeShortAnswers.choices()
                else:
                    choices = SchemaGenericAnswers.choices()

                form_field = forms.ChoiceField(
                    choices=choices,
                    label=field["question"],
                    widget=forms.RadioSelect(choices=choices),
                )

            self.fields[f"field_{index}"] = form_field

    def save(self, commit=True):
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

    class Meta:
        model = Submission
        fields = []
