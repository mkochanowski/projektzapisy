# -*- coding: utf-8 -*-

"""
    Django admin panel for vote
"""

from datetime import date

from django.contrib import admin
from django.forms   import ModelForm
from django.forms   import ValidationError

from apps.offer.vote.models import SystemState, SingleVote

class SystemStateAdminForm( ModelForm ):
    """
        Admin form for system state
    """
    class Meta:
        model = SystemState
        
    def clean_year(self):
        """
            Year validation
        """
        data = self.cleaned_data['year']
        
        if data < date.today().year:
            raise ValidationError("Podano miniony rok.")
            
        return data
        
    def clean_max_points(self):
        """
            Max points per subjects validation
        """
        data = self.cleaned_data['max_points']
        
        if data < 1:
            raise ValidationError("Musi wynosić co najmniej 1.")
            
        return data
        
    def clean_max_vote(self):
        """
            Max vote value validation
        """
        data = self.cleaned_data['max_vote']
        max_points_name = SystemState._meta.get_field_by_name('max_points')[0].verbose_name
        try:
            aux = self.cleaned_data['max_points']
        except KeyError:
            raise ValidationError(max_points_name + " nie jest \
                                    poprawnie ustawione. Nie można weryfikować.")
        
        if data < aux:
            raise ValidationError("Musi większa lub równa od " + max_points_name + ".")
               
        return data
        
    def clean_vote_beg(self):
        """
            Vote beggining validation
        """
        data = self.cleaned_data['vote_beg']
        
        year_name = SystemState._meta.get_field_by_name('year')[0].verbose_name
        
        try:
            aux = self.cleaned_data['year']
        except KeyError:
            raise ValidationError( year_name + 
                        " nie jest poprawnie ustawiony. Nie można weryfikować.")
        
        if data.year != aux:
            raise ValidationError("Rok otwarcia głosowania musi być taki sam\
                                    jak " + year_name + ".")
        
        return data
        
    def clean_vote_end(self):
        """
            Vote ending validation
        """
        data = self.cleaned_data['vote_end']
        
        year_name = SystemState._meta.get_field_by_name('year')[0].verbose_name
        vote_beg_name = SystemState._meta.get_field_by_name('vote_beg')[0].verbose_name
        
        try:
            aux = self.cleaned_data['year']
        except KeyError:
            raise ValidationError( year_name + 
                        " nie jest poprawnie ustawiony. Nie można weryfikować.")
        
        if data.year != aux:
            raise ValidationError("Rok zakonczenia głosowania musi być taki sam\
                                    jak " + year_name + ".")
        
        try:
            aux = self.cleaned_data['vote_beg']
        except KeyError:
            raise ValidationError( vote_beg_name + 
                        " nie jest poprawnie ustawiony. Nie można weryfikować.")
                        
        if data <= aux:
            raise ValidationError( "Musi być przynajmniej o dzień później \
                                    niż " + vote_beg_name + ".")
                                    
        return data

class StateAdmin( admin.ModelAdmin ):
    """
        System State Administration
    """
    form = SystemStateAdminForm

admin.site.register( SystemState, StateAdmin )
admin.site.register( SingleVote )


