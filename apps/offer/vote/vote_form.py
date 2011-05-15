# -*- coding: utf-8 -*-

"""
    Form for vote
"""

from django                   import forms
from django.core.exceptions   import ObjectDoesNotExist
from django.utils.safestring  import SafeUnicode

from apps.offer.vote.models import SystemState
from apps.offer.vote.models import SingleVote
from django.core.urlresolvers import reverse

class VoteField(forms.ChoiceField):
    def __init__(self, choices=(), required=True, widget=None, label=None,
                 initial=None, help_text=None, url='', *args, **kwargs):
        super(VoteField, self).__init__(required=required, widget=widget, label=label,
                                        choices=choices,
                                        initial=initial, help_text=help_text, *args, **kwargs)
        self.url = url

class VoteForm( forms.Form ):
    """
        Voting form
    """
    choices = [(str(i), i) for i in range(SystemState.get_max_points()+1)]
    course_types = {}
    course_fan_flag = {}
    
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
                            course = sub,
                            state   = state ).value
            except ObjectDoesNotExist:
                choosed = 0
            
            self.fields['winter_%s' % sub.pk] = VoteField(
                                            label     = sub.name,
                                            url       = reverse('proposal-page', args=[sub.slug]),
                                            choices   = self.choices,
                                            help_text = u'Semestr Zimowy',
                                            initial   = choosed)
            self.course_types['winter_%s' % sub.pk] = sub.description().types()
            self.course_fan_flag['winter_%s' % sub.pk] = sub.is_in_group(voter, 'fans')
                                            
        for sub in summer:
            try:
                choosed = SingleVote.objects.get( 
                            student = voter, 
                            course = sub,
                            state   = state ).value
            except ObjectDoesNotExist:
                choosed = 0
            
            self.fields['summer_%s' % sub.pk] = VoteField(
                                            label     = sub.name,
                                            url       = reverse('proposal-page', args=[sub.slug]),
                                            choices   = self.choices,
                                            help_text = u'Semestr Letni',
                                            initial   = choosed)
            self.course_types['summer_%s' % sub.pk] = sub.description().types()
            self.course_fan_flag['summer_%s' % sub.pk] = sub.is_in_group(voter, 'fans')
        
        for sub in unknown:
            try:
                choosed = SingleVote.objects.get( 
                            student = voter, 
                            course = sub,
                            state   = state ).value
            except ObjectDoesNotExist:
                choosed = 0
            
            self.fields['unknown_%s' % sub.pk] = VoteField(
                                            label     = sub.name,
                                            url       = reverse('proposal-page', args=[sub.slug]),
                                            choices   = self.choices,
                                            help_text = u'Semestr Nieokreślony',
                                            initial   = choosed)
            self.course_types['unknown_%s' % sub.pk] = sub.description().types()
            self.course_fan_flag['unknown_%s' % sub.pk] = sub.is_in_group(voter, 'fans')
    
    def vote_points( self ):
        """
            Calculates points
        """
        for name, value in self.cleaned_data.items():
            if name.startswith('winter_') or \
               name.startswith('summer_') or \
               name.startswith('unknown_'):
                yield (self.fields[name].label, value)
    
    def as_lists( self ):
        """
            Creates html form
        """
        winter   = u'<div class="od-vote-semester" id="od-vote-semester-winter"><h2>Semestr zimowy</h2><ul>'
        summer   = u'<div class="od-vote-semester" id="od-vote-semester-summer"><h2>Semestr letni</h2><ul>'
        unknown  = u'<div class="od-vote-semester" id="od-vote-semester-unknown"><h2>Semestr nieokreślony</h2><ul>'

        winter_empty = True
        summer_empty = True
        unknown_empty = True
        
        maksimum  = u'<p id="od-vote-maxPoints">Maksymalna liczba punktów do wykorzystania: <span>'
        maksimum += str(SystemState.get_max_vote())
        maksimum += u' </span></p>'
        
        for key in self.fields.iterkeys():
            field = self.fields[key]

            course_class = u''
            for type in self.course_types[key]:
                course_class += u' course-type-' + str(type.lecture_type.id)
            if self.course_fan_flag[key]:
                course_class += " isFan"
            field_str = \
                u'<li class="od-vote-course ' + course_class + '">\
                    <label for="id_' + key + '"><a href="'+ field.url +'">' + field.label + '</a></label>\
                    <select name="' + key + '" id="id_' + key + '">'
            for (i, s) in field.choices:
                field_str += '<option value="'
                field_str += str(i)
                field_str += '"' 
                if i == str(field.initial):
                    field_str += ' selected="selected"'
                field_str += '>'
                field_str += str(s)
                field_str += '</option>'
            field_str += ' </select></li>'
                    
            if   key.startswith('winter_'):
                winter_empty = False
                winter += field_str
            elif key.startswith('summer_'):
                summer_empty = False
                summer += field_str
            elif key.startswith('unknown_'):
                unknown_empty = False
                unknown += field_str

        list = SafeUnicode(u'')
        if (not winter_empty):
            list += SafeUnicode(winter) + SafeUnicode(u'</ul></div>')
        if (not summer_empty):
            list += SafeUnicode(summer) + SafeUnicode(u'</ul></div>')
        if (not unknown_empty):
            list += SafeUnicode(unknown) + SafeUnicode(u'</ul></div>')

        return  list + SafeUnicode(maksimum)
