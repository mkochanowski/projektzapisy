# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from apps.users.models import StudiaZamawiane, Employee


class EmailChangeForm(forms.ModelForm):
    class Meta:
        fields = ['email']
        model = User

class BankAccountChangeForm(forms.ModelForm):
    class Meta:
        fields = ['bank_account']
        model = StudiaZamawiane

class ConsultationsChangeForm(forms.ModelForm):
    class Meta:
        fields = ['room','homepage','consultations']
        model = Employee