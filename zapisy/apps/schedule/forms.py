# -*- coding: utf-8 -*-
from django                   import forms
from django.db.models.query import EmptyQuerySet
from apps.enrollment.courses.models import Course, Semester
from apps.schedule.models import Event, types_for_student, types_for_teacher, Term, EventModerationMessage, EventMessage

from django.forms.models import inlineformset_factory

TermFormSet = inlineformset_factory(Event, Term, extra=0)

class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        exclude = ('status', 'author', 'created', 'edited')

    def __init__(self, user, **kwargs):
        super(EventForm, self).__init__(**kwargs)
        self.author = user
        if user.employee:
            self.fields['type'].choices = types_for_teacher
        else:
            self.fields['type'].choices = types_for_student

        if not user.employee:
            self.fields['course'].queryset = EmptyQuerySet()
        else:
            semester = Semester.get_current_semester()
            self.fields['course'].queryset = Course.objects.filter(teachers=user.employee, semester=semester)

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

