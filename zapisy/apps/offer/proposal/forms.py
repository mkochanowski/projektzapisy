# -*- coding: utf-8 -*-
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import ModelForm
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription


class ProposalForm(ModelForm):
    class Meta:
        fields = ('name', 'type', 'exam', 'english', 'semester', 'web_page', 'status' )
        model = CourseEntity


class ProposalDescriptionForm(ModelForm):
    class Meta:
        fields = ('description', 'requirements', 'is_ready')
        model = CourseDescription
        widgets = {
            'requirements': FilteredSelectMultiple("wymagania", is_stacked=False)
        }

