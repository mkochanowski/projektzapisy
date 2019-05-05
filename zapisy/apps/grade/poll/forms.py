from django.forms import ModelForm, Form
from django import forms

# from django_jsonforms.forms import JSONSchemaField
from .models import Submission

# class SubmissionEntryForm(forms.Form):
#     # submission = Submission.objects.first()
#     json = JSONSchemaField(
# schema = submission.answers,
#         schema = {
#   "title": "Person",
#   "type": "object",
#   "required": [
#     "name",
#     "age",
#     "date",
#     "favorite_color",
#     "gender",
#     "location",
#     "pets"
#   ],
#   "properties": {
#     "name": {
#       "type": "string",
#       "description": "First and Last name",
#       "minLength": 4,
#       "default": "Jeremy Dorn"
#     },
#     "age": {
#       "type": "integer",
#       "default": 25,
#       "minimum": 18,
#       "maximum": 99
#     },
#     "favorite_color": {
#       "type": "string",
#       "format": "color",
#       "title": "favorite color",
#       "default": "#ffa500"
#     },
#     "gender": {
#       "type": "string",
#       "enum": [
#         "male",
#         "female"
#       ]
#     },
#     "date": {
#       "type": "string",
#       "format": "date",
#       "options": {
#         "flatpickr": {}
#       }
#     },
#     "location": {
#       "type": "object",
#       "title": "Location",
#       "properties": {
#         "city": {
#           "type": "string",
#           "default": "San Francisco"
#         },
#         "state": {
#           "type": "string",
#           "default": "CA"
#         },
#         "citystate": {
#           "type": "string",
#           "description": "This is generated automatically from the previous two fields",
#           "template": "{{city}}, {{state}}",
#           "watch": {
#             "city": "location.city",
#             "state": "location.state"
#           }
#         }
#       }
#     },
#     "pets": {
#       "type": "array",
#       "format": "table",
#       "title": "Pets",
#       "uniqueItems": True,
#       "items": {
#         "type": "object",
#         "title": "Pet",
#         "properties": {
#           "type": {
#             "type": "string",
#             "enum": [
#               "cat",
#               "dog",
#               "bird",
#               "reptile",
#               "other"
#             ],
#             "default": "dog"
#           },
#           "name": {
#             "type": "string"
#           }
#         }
#       },
#       "default": [
#         {
#           "type": "dog",
#           "name": "Walter"
#         }
#       ]
#     }
#   }
# },
#         options = {"theme": "bootstrap3"},
#     )


class TicketsEntryForm(forms.Form):
    tickets = forms.CharField(widget=forms.Textarea)


class SubmissionEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.jsonfields = kwargs.pop("jsonfields", None)
        super().__init__(*args, **kwargs)

        for field in self.jsonfield:
            f = forms.CharField(label=field["name"], required=False)
            self.fields[field["slug"]] = f

    def save(self, commit=True):
        d = {}
        for field in self.jsonfields:
            v = self.cleaned_data.get(field.slug)
            d[field.slug] = v

        self.instance.fields = d

        return super().save(commit)

    class Meta:
        model = Submission
        fields = []


# class SemesterGradeForm(forms.ModelForm):

