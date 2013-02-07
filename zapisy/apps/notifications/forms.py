# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import modelformset_factory
from apps.notifications.models import NotificationPreferences

__author__ = 'maciek'

BOOL_CHOICES = ((True, 'Tak'), (False, 'Nie'))

class NotificationForm(forms.ModelForm):

    class Meta:
        fields = ('value',)
        model = NotificationPreferences
        widgets = {
                    'value': forms.RadioSelect(choices=BOOL_CHOICES)
                }


NotificationFormset = modelformset_factory(NotificationPreferences, form=NotificationForm, extra=0, can_delete=False)
