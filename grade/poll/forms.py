# -*- coding: utf-8 -*-
"""
    Forms used to grade courses
"""
from django                   import forms
from django.utils.safestring  import SafeUnicode
from django.core.exceptions   import ValidationError, \
                                     ObjectDoesNotExist
from django.core.validators   import MaxLengthValidator                                     

from fereol.grade.poll.models import SingleChoiceQuestionOrdering

from fereol.grade.poll.models import OpenQuestionAnswer, \
                                     SingleChoiceQuestionAnswer, \
                                     MultipleChoiceQuestionAnswer

class TicketsForm( forms.Form ):
    ticketsfield = forms.CharField( widget = forms.widgets.Textarea( 
                                                    attrs = {'cols' : 80, 
                                                             'rows' : 20 }), 
                                 label     = "Podaj wygenerowane klucze",
                                 help_text = "Wklej tutaj pobrane wcześniej klucze." )

class PollForm( forms.Form ):
    def setFields( self, poll, st ):
        self.finished = st.finished
        for section in poll.all_sections():
            title     = 'poll-%d_section-%d' % ( poll.pk, section.pk )
            questions = section.all_questions()
            
            if str( type( questions[ 0 ])) == \
                "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestion'>":
                if SingleChoiceQuestionOrdering.objects.get( 
                        sections = section,
                        question = questions[ 0 ]).is_leading:
                    title += '_question-%d-leading' % questions[ 0 ].pk
                    
                    try:
                        answer = SingleChoiceQuestionAnswer.objects.get( 
                                    saved_ticket = st,
                                    section      = section,
                                    question     = questions[ 0 ] ).option.pk
                    except ObjectDoesNotExist:
                        answer = None
                    
                    choices = []
                    for option in questions[ 0 ].options.all():
                        choices.append(( option.pk, unicode( option.content )))
                    field = forms.ChoiceField( 
                                choices  = choices,
                                label    = unicode( questions[ 0 ].content ),
                                required = False,
                                widget   = forms.widgets.RadioSelect(),
                                initial  = answer )
                    field.widget.attrs[ 'disabled' ] = self.finished
                    self.fields[ unicode( title ) ]  = field
                    questions = questions[ 1: ]
                    
            for question in questions:
                title = 'poll-%d_section-%d_question-%d' % ( poll.pk, section.pk, question.pk )
                if str( type( question )) == \
                    "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestion'>":
                    title += '-single'
                    
                    if question.is_scale:
                        title += '-scale'

                    try:
                        answer = SingleChoiceQuestionAnswer.objects.get( 
                                    saved_ticket = st,
                                    section      = section,
                                    question     = question )
                    except ObjectDoesNotExist:
                        answer = None
                        
                    choices = []
                    for option in question.options.all():
                        choices.append(( option.pk, unicode( option.content )))
                    field = forms.ChoiceField( choices  = choices,
                                               label    = unicode( question.content ),
                                               required = False,
                                               widget   = forms.widgets.RadioSelect(),
                                               initial  = answer )
                    field.widget.attrs[ 'disabled' ] = self.finished
                    self.fields[ unicode( title ) ] = field
                elif str( type( question )) == \
                    "<class 'fereol.grade.poll.models.multiple_choice_question.MultipleChoiceQuestion'>":
                    title += '-multi'
                    
                    try:
                        answer   = MultipleChoiceQuestionAnswer.objects.get(
                                      saved_ticket = st,
                                      section      = section,
                                      question     = question)
                        other_ans = answer.other
                        answer    =  map( lambda x: x.pk, answer.options.all())
                    except ObjectDoesNotExist:
                        answer    = None
                        other_ans = None
                    
                    choices = []
                    for option in question.options.all():
                        choices.append(( option.pk, unicode( option.content )))
                    
                    if question.has_other:
                        choices.append(( -1, unicode( 'Inne' )))
                        other_field = forms.CharField( 
                                        label    = u'', 
                                        initial  = other_ans,
                                        required = False )
                        other_field.widget.attrs[ 'disabled' ] = self.finished
                        if other_ans: answer.append( -1 )
                    
                    field = forms.MultipleChoiceField( 
                                choices    = choices,
                                label      = unicode( question.content ),
                                required   = False,
                                widget     = forms.widgets.CheckboxSelectMultiple(),
                                initial    = answer,
                                validators = [ MaxLengthValidator( question.choice_limit )])
                    field.widget.attrs[ 'disabled' ] = self.finished
                    self.fields[ unicode( title ) ] = field
                    if question.has_other:
                        self.fields[ unicode( title + '-other' ) ] = other_field
                elif str( type( question )) == \
                    "<class 'fereol.grade.poll.models.open_question.OpenQuestion'>":
                    title += '-open'
                    
                    try:
                        answer = OpenQuestionAnswer.objects.get( 
                                    saved_ticket = st,
                                    section      = section,
                                    question     = question ).content
                    except ObjectDoesNotExist:
                        answer = ""
    
                    field = forms.CharField( 
                                widget = forms.widgets.Textarea(
                                                attrs = { 'cols'  : 80,
                                                          'rows'  : 20 }),
                                label  = unicode( question.content ),
                                required = False,
                                initial  = answer )
                    field.widget.attrs[ 'disabled' ] = self.finished
                    self.fields[ unicode( title ) ] = field
        
        if not self.finished:
            field = forms.BooleanField(
                            label     = u'Zakończ oceniać',
                            required  = False,
                            initial   = False,
                            help_text = u'Jeśli zaznaczysz to pole, utracisz mozliwość edycji ankiety po zapisaniu.' )
            self.fields[ u'finish' ] = field
    
