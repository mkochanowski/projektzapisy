from django.forms import ModelForm, Form
from django import forms

# from django_jsonforms.forms import JSONSchemaField
from .models import Submission


class TicketsEntryForm(forms.Form):
    tickets = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(TicketsEntryForm, self).__init__(*args, **kwargs)
        self.fields["tickets"].widget.attrs["class"] = "form-control"


CHOICES_PERSONAL_EVALUATION = [
    ("definately_better", "zdecydowanie lepsze"),
    ("better", "trochę lepsze"),
    ("neutral", "mniej więcej takie same"),
    ("worse", "trochę gorsze"),
    ("definately_worse", "zdecydowanie gorsze"),
]
CHOICES_TIME_STRETCHED = [
    ("few_hours", "kilka godzin"),
    ("one_day", "około 1 dnia"),
    ("a_few_days", "kilka dni (około 3)"),
    ("almost_a_week", "prawie cały tydzień"),
]
CHOICES_TIME_SHORT = [
    ("less_than_one_hour", "mniej niż 1 godzinę"),
    ("about_two_hours", "około 2 godzin"),
    ("about_five_hours", "jedno popołudnie (około 5 godzin)"),
    ("about_ten_hours", "dwa popołudnia (około 10 godzin)"),
    ("more_than_two_days", "więcej niż dwa dni"),
]
CHOICES_GRADE = [
    ("strongly_agree", "zdecydowanie tak"),
    ("agree", "raczej tak"),
    ("neutral", "trudno powiedzieć"),
    ("disagree", "raczej nie"),
    ("strongly_disagree", "zdecydowanie nie"),
]


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
                    choices = CHOICES_PERSONAL_EVALUATION
                elif field["type"] == "predefined_choices_time_stretched":
                    choices = CHOICES_TIME_STRETCHED
                elif field["type"] == "predefined_choices_time_short":
                    choices = CHOICES_TIME_SHORT
                else:
                    choices = CHOICES_GRADE
                form_field = forms.CharField(
                    label=field["question"],
                    widget=forms.RadioSelect(choices=choices),
                    required=True,
                )

            self.fields[f"field_{index}"] = form_field

    def save(self, commit=True):
        d = {}
        updated_answers = self.instance.answers
        for index, field in enumerate(self.jsonfields):
            field_name = f"field_{index}"
            # print("field_name:", field_name, "field:", field)
            updated_answers["schema"][index] = {
                "question": field["question"],
                "type": field["type"],
                "answer": self.cleaned_data.get(field_name),
            }
            # v = self.cleaned_data.get(field_name)
            # d[field_name] = v

        self.instance.answers = updated_answers

        return super().save(commit)

    def get_success_url(self):
        return reverse("grade-poll-v2-submissions")

    class Meta:
        model = Submission
        fields = []


# class SemesterGradeForm(forms.ModelForm):

