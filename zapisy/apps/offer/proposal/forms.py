# -*- coding: utf-8 -*-
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import ModelForm
from django import forms
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription
from apps.offer.proposal.models import Syllabus, StudentWork


class ProposalForm(ModelForm):
    ects = forms.IntegerField(label='ECTS')

    def __init__(self, *args, **kwargs):
        full_edit = kwargs.pop('full_edit', False)
        super(ProposalForm, self).__init__(*args, **kwargs)
        if not full_edit:
            self.fields['lectures'].widget.attrs['readonly'] = True
            self.fields['repetitions'].widget.attrs['readonly'] = True
            self.fields['exercises'].widget.attrs['readonly'] = True
            self.fields['laboratories'].widget.attrs['readonly'] = True
            self.fields['exercises_laboratiories'].widget.attrs['readonly'] = True
            self.fields['seminars'].widget.attrs['readonly'] = True
            self.fields['ects'].widget.attrs['readonly'] = True

    class Meta:
        fields = ('name', 'name_en', 'type', 'exam', 'english', 'semester', 'web_page','effects', 'repetitions', 'lectures', 'exercises', 'laboratories', 'exercises_laboratiories', 'seminars')
        model = CourseEntity
        widgets = {
            'effects': FilteredSelectMultiple(u"efekty kształcenia", is_stacked=False)
        }

class ProposalDescriptionForm(ModelForm):
    class Meta:
        fields = ('description', 'requirements')
        model = CourseDescription
        widgets = {
            'description': forms.Textarea(attrs={'class': 'tinymce'}),
            'requirements': FilteredSelectMultiple("wymagania", is_stacked=False)
        }

class SyllabusForm(ModelForm):
    class Meta:
        fields = ('requirements', 'studies_type', 'year', 'requirements', 'objectives', 'effects_txt', 'contents', 'learning_methods', 'literature', 'passing_form')
        model = Syllabus
        widgets = {
            'learning_methods': FilteredSelectMultiple(u"Metody kształcenia", is_stacked=False)
        }