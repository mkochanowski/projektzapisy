# -*- coding: utf-8 -*-
from copy import deepcopy
from django                   import forms
from django.db.models.query import EmptyQuerySet
from django.forms import HiddenInput
from apps.enrollment.courses.models import Course, Semester
from apps.schedule.models import Event, types_for_student, types_for_teacher, Term, EventModerationMessage, EventMessage

from django.forms.models import inlineformset_factory


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        widgets = {
            'event': HiddenInput(),
            'day': HiddenInput(),
            'start': HiddenInput(),
            'end': HiddenInput(),
            'room': HiddenInput(),
            'place': HiddenInput()

        }

TermFormSet = inlineformset_factory(Event, Term, extra=0, form=TermForm)

class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        exclude = ('status', 'author', 'created', 'edited', 'group', 'interested')

    def __init__(self, user, data=None, **kwargs):

        if data:
            data = deepcopy(data)
            if 'type' not in data:
                data['type'] = '2'


        super(EventForm, self).__init__(data, **kwargs)

        self.author = user

        if user.employee:
            self.fields['type'].choices = types_for_teacher
        else:
            self.fields['type'].choices = types_for_student

        if not user.employee:
            self.fields['course'].queryset = EmptyQuerySet()

        else:
            semester = Semester.get_current_semester()
            qs  = Course.objects.filter(semester=semester)
            if not user.has_perm('schedule.manage_events'):
                qs = qs.filter(teachers=user.employee)

            self.fields['course'].queryset = qs

        self.fields['title'].widget.attrs.update({'class' : 'span7'})
        self.fields['type'].widget.attrs.update({'class' : 'span7'})
        self.fields['course'].widget.attrs.update({'class' : 'span7'})
        self.fields['description'].widget.attrs.update({'class' : 'span7', 'required': 'required'})

class EventModerationMessageForm(forms.ModelForm):
    class Meta:
        model = EventModerationMessage
        fields = ('message', )

class EventMessageForm(forms.ModelForm):
    class Meta:
        model = EventMessage
        fields = ('message', )

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('status',)

