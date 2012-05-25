# -*- coding: utf-8 -*-
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import ModelForm
from apps.enrollment.courses.models.course import CourseEntity


class ProposalForm(ModelForm):
    class Meta:
        exclude=('slug', 'owner', 'hidden', 'deleted', 'student')
        model = CourseEntity
        widgets = {
            'requirements': FilteredSelectMultiple("wymagania", is_stacked=False)
        }

