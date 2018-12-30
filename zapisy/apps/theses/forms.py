from dal import autocomplete
from django import forms

from .models import Thesis


class ThesisForm(forms.ModelForm):
    """A custom admin form for thesis objects.
    While users are generally expected to use the React-based frontend
    and not the Django admin interface, occasionally the admin may want
    to view one there. Because there are so many users/employees in the system,
    the <select> widget Django outputs lags the browser, so we use
    https://github.com/yourlabs/django-autocomplete-light to mitigate that problem
    by fetching users via AJAX.

    Note that frontend client code reuses the endpoint provided by DAL for the same
    purpose; see backend_callers.ts
    """

    class Meta:
        model = Thesis
        fields = "__all__"
        widgets = {
            "student": autocomplete.ModelSelect2(url="theses:student-autocomplete"),
            "student_2": autocomplete.ModelSelect2(url="theses:student-autocomplete"),
            "advisor": autocomplete.ModelSelect2(url="theses:employee-autocomplete"),
            "auxiliary_advisor": autocomplete.ModelSelect2(url="theses:employee-autocomplete")
        }
