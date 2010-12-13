# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User


class EmailChangeForm(forms.ModelForm):
    class Meta:
        fields = ['email']
        model = User