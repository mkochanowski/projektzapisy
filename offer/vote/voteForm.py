# -*- coding: utf-8 -*-

from django                   import forms
from django.core.exceptions   import ObjectDoesNotExist
from django.utils.safestring  import SafeUnicode

from fereol.offer.vote.models import SystemState
from fereol.offer.vote.models import SingleVote


class VoteForm( forms.Form ):
    choices = [(str(i), i) for i in range(SystemState.get_maxPoints()+1)]
    
    def __init__ (self, *args, **kwargs):
        winter  = kwargs.pop('winter')
        summer  = kwargs.pop('summer')
        unknown = kwargs.pop('unknown')
        voter   = kwargs.pop('voter')
        
        state   = SystemState.get_state()
        
        super(VoteForm, self).__init__(*args, **kwargs)

        for sub in winter:
            try:
                choosed = SingleVote.objects.get( 
                            student = voter, 
                            subject = sub,
                            state   = state ).value
            except ObjectDoesNotExist:
                choosed = 0
            
            self.fields['winter_%s' % sub.pk] = forms.ChoiceField(
                                            label     = sub.name,
                                            choices   = self.choices,
                                            help_text = u'Semestr Zimowy',
                                            initial   = choosed)
                                            
        for sub in summer:
            try:
                choosed = SingleVote.objects.get( 
                            student = voter, 
                            subject = sub,
                            state   = state ).value
            except ObjectDoesNotExist:
                choosed = 0
            
            self.fields['summer_%s' % sub.pk] = forms.ChoiceField(
                                            label     = sub.name,
                                            choices   = self.choices,
                                            help_text = u'Semestr Letni',
                                            initial   = choosed)
        
        for sub in unknown:
            try:
                choosed = SingleVote.objects.get( 
                            student = voter, 
                            subject = sub,
                            state   = state ).value
            except ObjectDoesNotExist:
                choosed = 0
            
            self.fields['unknown_%s' % sub.pk] = forms.ChoiceField(
                                            label     = sub.name,
                                            choices   = self.choices,
                                            help_text = u'Semestr Nieokreślony',
                                            initial   = choosed)
    
    def vote_points( self ):
        for name, value in self.cleaned_data.items():
            if name.startswith('winter_') or \
               name.startswith('summer_') or \
               name.startswith('unknown_'):
                yield (self.fields[name].label, value)
    
    def as_table( self ):
        #str = super(forms.Form, self).as_table()
        #print str
        #return str
        winter   = u'<tr><th>Semestr Zimowy</th><th></th></tr>'
        summer   = u'<tr><th>Semestr Letni</th><th></th></tr>'
        unknown  = u'<tr><th>Semestr Nieokreślony</th><th></th></tr>'
        
        maksimum  = u'<tr><th>Maksymalna liczba punktów:</th><td>'
        maksimum += str(SystemState.get_maxVote())
        maksimum += u'</td></th>'
        
        
        for key in self.fields.iterkeys():
            field = self.fields[key]
            field_str = \
                u'<tr>\
                    <td><label for="id_' + key + '">' + field.label + '</td>\
                    <td><select name="' + key + '" id="id_' + key + '">'
            for (i, s) in field.choices:
                field_str += '<option value="'
                field_str += str(i)
                field_str += '"' 
                if i == str(field.initial):
                    field_str += ' selected="selected"'
                field_str += '>'
                field_str += str(s)
                field_str += '</option>'
            field_str += '</select></td></tr>'
                    
            if   key.startswith('winter_'):
                winter += field_str
            elif key.startswith('summer_'):
                summer += field_str
            elif key.startswith('unknown_'):
                unknown += field_str
                
        wyn  =  SafeUnicode(winter) + \
                SafeUnicode(summer) + \
                SafeUnicode(unknown) + \
                SafeUnicode(maksimum)
        print wyn
        return wyn
