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
            Max points per courses validation
        """
        data = self.cleaned_data['max_points']
        
        if data < 1:
            raise ValidationError("Musi wynosić co najmniej 1.")
            
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

class SingleVoteAdmin( admin.ModelAdmin ):
    raw_id_fields = ('student', )
    list_display = ('student', 'entity', 'course','correction', 'state')
    list_filter = ('correction', 'state', 'entity', 'course__semester')
    search_fields = ('student__matricula', 'student__user__first_name', 'student__user__last_name', 'student__user__username', 'entity__name', 'course__name')

    def queryset(self, request):
       """
       Filter the objects displayed in the change_list to only
       display those for the currently signed in user.
       """
       qs = super(SingleVoteAdmin, self).queryset(request)
       return qs.select_related('student', 'student__user', 'course', 'course__semester', 'course__type', 'entity',
           'proposal', 'state')

class StateAdmin( admin.ModelAdmin ):
    """
        System State Administration
    """
    form = SystemStateAdminForm

admin.site.register( SystemState, StateAdmin )
admin.site.register( SingleVote, SingleVoteAdmin )
