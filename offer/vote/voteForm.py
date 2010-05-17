# -*- coding: utf-8 -*-

from django                  import forms
from django.utils.safestring import SafeUnicode
from fereol.offer.vote.models import SystemState

class VoteForm( forms.Form ):
    choices = [(str(i), i) for i in range(SystemState.get_maxPoints()+1)]
    
    def __init__ (self, *args, **kwargs):
        winter  = kwargs.pop('winter')
        summer  = kwargs.pop('summer')
        unknown = kwargs.pop('unknown')
        super(VoteForm, self).__init__(*args, **kwargs)

        for (i, sub) in enumerate(winter):
            self.fields['winter_%s' % i] = forms.ChoiceField(
                                            label     = sub.name,
                                            choices   = self.choices,
                                            help_text = u'Semestr Zimowy')
                                            
        for (i, sub) in enumerate(summer):
            self.fields['summer_%s' % i] = forms.ChoiceField(
                                            label     = sub.name,
                                            choices   = self.choices,
                                            help_text = u'Semestr Letni')
        
        for (i, sub) in enumerate(unknown):
            self.fields['unknown_%s' % i] = forms.ChoiceField(
                                            label     = sub.name,
                                            choices   = self.choices,
                                            help_text = u'Semestr Nieokreślony')
    
    def vote_points( self ):
        for name, value in self.cleaned_data.items():
            if name.startswith('winter_') or \
               name.startswith('summer_') or \
               name.startswith('unknown_'):
                yield (self.fields[name].label, value)
    
    def as_table( self ):
        winter  = u'<tr><th>Semestr Zimowy</th><th></th></tr>'
        summer  = u'<tr><th>Semestr Letni</th><th></th></tr>'
        unknown = u'<tr><th>Semestr Nieokreślony</th><th></th></tr>'
        
        for key in self.fields.iterkeys():
            field = self.fields[key]
            field_str = \
                u'<tr>\
                    <td><label for="id_' + key + '">' + field.label + '</td>\
                    <td><select name="' + key + '" id="id_' + key + '">'
            for (i, s) in field.choices:
                field_str += '<option value="'
                field_str += str(i) 
                field_str += '">'
                field_str += str(s)
                field_str += '</option>'
            field_str += '</select></td></tr>'
                    
            if   key.startswith('winter_'):
                winter += field_str
            elif key.startswith('summer_'):
                summer += field_str
            elif key.startswith('unknown_'):
                unknown += field_str
                
        return  SafeUnicode(winter) + \
                SafeUnicode(summer) + \
                SafeUnicode(unknown)

