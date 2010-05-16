# -*- coding: utf-8 -*-

from django import forms

from fereol.offer.vote.models import SystemState

class VoteForm( forms.Form ):
    choices = [(i, str(i)) for i in range(SystemState.get_maxPoints()+1)]
    
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
