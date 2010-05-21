# -*- coding: utf-8 -*-

from django                   import forms
from django.utils.safestring  import SafeUnicode
from fereol.offer.vote.models import SystemState

class VoteForm( forms.Form ):
    choices = [(str(i), i) for i in range(SystemState.get_maxPoints()+1)]
    
    def __init__ (self, *args, **kwargs):
        winter  = kwargs.pop('winter')
        summer  = kwargs.pop('summer')
        unknown = kwargs.pop('unknown')
        super(VoteForm, self).__init__(*args, **kwargs)

        for sub in winter:
            self.fields['winter_%s' % sub.pk] = forms.ChoiceField(
                                            label     = sub.name,
                                            choices   = self.choices,
                                            help_text = u'Semestr Zimowy')
                                            
        for sub in summer:
            self.fields['summer_%s' % sub.pk] = forms.ChoiceField(
                                            label     = sub.name,
                                            choices   = self.choices,
                                            help_text = u'Semestr Letni')
        
        for sub in unknown:
            self.fields['unknown_%s' % sub.pk] = forms.ChoiceField(
                                            label     = sub.name,
                                            choices   = self.choices,
                                            help_text = u'Semestr Nieokreślony')
    
    def vote_points( self ):
        for name, value in self.cleaned_data.items():
            if name.startswith('winter_') or \
               name.startswith('summer_') or \
               name.startswith('unknown_'):
                yield (self.fields[name].label, value)
    
    def as_lists( self ):
        winter   = u'<div class="od-vote-semester" id="od-vote-semester-winter"><h2>Semestr Zimowy</h2><ul>'
        summer   = u'<div class="od-vote-semester" id="od-vote-semester-summer"><h2>Semestr Letni</h2><ul>'
        unknown  = u'<div class="od-vote-semester" id="od-vote-semester-unknown"><h2>Semestr Nieokreślony</h2><ul>'

        winterEmpty = True
        summerEmpty = True
        unknownEmpty = True
        
        maksimum  = u'<p id="od-vote-maxPoints">Maksymalna liczba punktów:'
        maksimum += str(SystemState.get_maxVote())
        maksimum += u'</p>'
        
        for key in self.fields.iterkeys():
            field = self.fields[key]
            field_str = \
                u'<li>\
                    <label for="id_' + key + '">' + field.label + '</label>\
                    <select name="' + key + '" id="id_' + key + '">'
            for (i, s) in field.choices:
                field_str += '<option value="'
                field_str += str(i) 
                field_str += '">'
                field_str += str(s)
                field_str += '</option>'
            field_str += ' </select></li>'
                    
            if   key.startswith('winter_'):
                winterEmpty = False
                winter += field_str
            elif key.startswith('summer_'):
                summerEmpty = False
                summer += field_str
            elif key.startswith('unknown_'):
                unknownEmpty = False
                unknown += field_str

        list = SafeUnicode(u'')
        if (not winterEmpty):
            list += SafeUnicode(winter) + SafeUnicode(u'</ul></div>')
        if (not summerEmpty):
            list += SafeUnicode(summer) + SafeUnicode(u'</ul></div>')
        if (not unknownEmpty):
            list += SafeUnicode(unknown) + SafeUnicode(u'</ul></div>')

        return  list + SafeUnicode(maksimum)

