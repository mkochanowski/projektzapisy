# -*- coding: utf-8 -*-
from datetime import date

from django.contrib import admin
from django.forms   import ModelForm
from django.forms   import ValidationError

from offer.vote.models import *

class SystemStateAdminForm( ModelForm ):
    class Meta:
        model = SystemState
        
    def clean_year(self):
        data = self.cleaned_data['year']
        
        if data < date.today().year:
            raise ValidationError("Podano miniony rok.")
            
        return data
        
    def clean_maxPoints(self):
        data = self.cleaned_data['maxPoints']
        
        if data < 1:
            raise ValidationError("Musi wynosić co najmniej 1.")
            
        return data
        
    def clean_maxVote(self):
        data = self.cleaned_data['maxVote']
        maxPoints_name = SystemState._meta.get_field_by_name('maxPoints')[0].verbose_name
        try:
            x = self.cleaned_data['maxPoints']
        except KeyError:
            raise ValidationError(maxPoints_name + " nie jest \
                                    poprawnie ustawione. Nie można weryfikować.")
        
        if data < x:
            raise ValidationError("Musi większa lub równa od " + maxPoints_name + ".")
               
        return data
        
    def clean_voteBeg(self):
        data = self.cleaned_data['voteBeg']
        
        year_name = SystemState._meta.get_field_by_name('year')[0].verbose_name
        
        try:
            x = self.cleaned_data['year']
        except KeyError:
            raise ValidationError( year_name + 
                        " nie jest poprawnie ustawiony. Nie można weryfikować.")
        
        if data.year != x:
            raise ValidationError("Rok otwarcia głosowania musi być taki sam\
                                    jak " + year_name + ".")
        
        return data
        
    def clean_voteEnd(self):
        data = self.cleaned_data['voteEnd']
        
        year_name = SystemState._meta.get_field_by_name('year')[0].verbose_name
        voteBeg_name = SystemState._meta.get_field_by_name('voteBeg')[0].verbose_name
        
        try:
            x = self.cleaned_data['year']
        except KeyError:
            raise ValidationError( year_name + 
                        " nie jest poprawnie ustawiony. Nie można weryfikować.")
        
        if data.year != x:
            raise ValidationError("Rok zakonczenia głosowania musi być taki sam\
                                    jak " + year_name + ".")
        
        try:
            x = self.cleaned_data['voteBeg']
        except KeyError:
            raise ValidationError( voteBeg_name + 
                        " nie jest poprawnie ustawiony. Nie można weryfikować.")
                        
        if data <= x:
            raise ValidationError( "Musi być przynajmniej o dzień później \
                                    niż " + voteBeg_name + ".")
                                    
        return data

class StateAdmin( admin.ModelAdmin ):
    form = SystemStateAdminForm

admin.site.register( SystemState, StateAdmin )
admin.site.register( SingleVote )


