from dal import autocomplete
from django import forms

from .models import Thesis


class ThesisForm(forms.ModelForm):
    class Meta:
        model = Thesis
        fields = ('__all__')
        widgets = {
            'student': autocomplete.ModelSelect2(url='theses:student-autocomplete'),
            'student_2': autocomplete.ModelSelect2(url='theses:student-autocomplete'),
            'advisor': autocomplete.ModelSelect2(url='theses:employee-autocomplete'),
            'auxiliary_advisor': autocomplete.ModelSelect2(url='theses:employee-autocomplete')
        }
