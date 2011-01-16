# -*- coding: utf-8 -*-
"""
    Forms used to grade courses
"""
from django                   import forms
from django.utils.safestring  import SafeUnicode
from django.core.exceptions   import ValidationError, \
                                     ObjectDoesNotExist

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

def open_question_field( question, section, saved_ticket ):
    try:
        answer = OpenQuestionAnswer.objects.get( saved_ticket = saved_ticket,
                                                 section      = section,
                                                 question     = question ).content
    except ObjectDoesNotExist:
        answer = ""
    
    field = forms.CharField( widget = forms.widgets.Textarea(
                                                    attrs = { 'cols'  : 80,
                                                              'rows'  : 20 }),
                             label  = unicode( question.content ),
                             required = False,
                             initial  = answer )
    
    return field

def single_choice_question_field( question, section, saved_ticket ):
    try:
        answer = SingleChoiceQuestionAnswer.objects.get( saved_ticket = saved_ticket,
                                                         section      = section,
                                                         question     = question )
    except:
        answer = None
        
    choices = []
    for option in question.options.all():
        choices.append(( option.pk, unicode( option.content )))
    field = forms.ChoiceField( choices  = choices,
                               label    = unicode( question.content ),
                               required = False,
                               widget   = forms.widgets.RadioSelect())
    
    if answer:
        field.initial = answer.option.pk
        
    return field

def multiple_choice_question_field( question, section, saved_ticket ):
    choices = []
    for option in question.options.all():
        choices.append(( option.pk, unicode( option.content )))
    if question.has_other: choices.append(( -1, 'Inne' ))
    
    try:
        answers = MultipleChoiceQuestionAnswer.objects.filter( saved_ticket = saved_ticket,
                                                               section      = section,
                                                               question     = question )
    except:
        answers = None
    
    field = forms.MultipleChoiceField( choices    = choices,
                                       label      = unicode( question.content ),
                                       required   = False,
                                       widget     = forms.widgets.CheckboxSelectMultiple())
    
    return field
    
class SectionForm( forms.Form ):
    test = forms.CharField( label = "test", initial = "test" )
    def __init__( self, *args, **kwargs ):
        #- 
        #- # MAJĄC TICKET POBIERZ WYPEŁNIENIE!
        #- # JEŚLI JEST ZAKOŃCZONY TICKET TO USTAW WSZYSTKIE POLA NA NIEAKTYWNE
        #- 
        #- section = kwargs.pop( 'section' )
        #- pollPk  = kwargs.pop( 'poll' )
        #- ticket  = kwargs.pop( 'ticket' )
        #- 
        super( SectionForm, self ).__init__( args, kwargs )
#- 
        #- self.title       = unicode( section )
        #- self.description = unicode( section.description )
        #- self.ticket      = ticket
        #- 
        #- all_questions    = section.all_questions()
#- 
        #- if str( type( all_questions[ 0 ] )) == \
               #- "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestion'>":
            #- if SingleChoiceQuestionOrdering.objects.get( sections = section, 
                                                         #- question = all_questions[ 0 ]).is_leading:
                #- field = single_choice_question_field( all_questions[ 0 ], section, ticket )
                #- self.fields[ 'leading_%d_%d' % ( pollPk, all_questions[0].pk )] = field
                #- all_questions = all_questions[ 1: ]
                    #- 
        #- for question in all_questions:
            #- if str( type( question )) == \
               #- "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestion'>":
                #- field = single_choice_question_field( question, section, ticket )
                #- title = 'question_%d_%d_single' % ( pollPk, question.pk )
                #- if question.is_scale: title += '_scale'
            #- elif str( type( question )) == \
                 #- "<class 'fereol.grade.poll.models.multiple_choice_question.MultipleChoiceQuestion'>":
                #- field = multiple_choice_question_field( question, section, ticket )
                #- title = 'question_%d_%d_multi' % ( pollPk, question.pk )
            #- elif str( type( question )) == \
                 #- "<class 'fereol.grade.poll.models.open_question.OpenQuestion'>":
                #- field = open_question_field( question, section, ticket )
               #- 
                #- try:
                    #- answer = OpenQuestionAnswer.objects.get( saved_ticket = ticket,
                                                             #- section      = section,
                                                             #- question     = question ).content
                #- except ObjectDoesNotExist:
                    #- answer = "default"
#- 
                #- field = forms.CharField( widget = forms.widgets.Textarea(
                                                                #- attrs = { 'cols'  : 80,
                                                                          #- 'rows'  : 20 }),
                                         #- label  = unicode( question.content ),
                                         #- required = False )
                #- title = 'question_%d_%d_open' % ( pollPk, question.pk )
            #- 
            #- self.fields[ title ] = field
            
    #- def as_table( self ):
        #- res  = u'<tr><th>' + unicode( self.title ) + u'<tr><th>'
        #- res += u'<tr><td>' + unicode( self.description ) + u'<tr><th>'
        #- 
        #- table = super( SectionForm, self ).as_table()
        #- table2 = table.split( u'Inne</label>' )
        #- for i, entry in enumerate( table2 ):
            #- if entry.startswith(u'</li>'):
                #- prev  = table2[ i - 1 ]
                #- prev  = prev.split( 'name="')
                #- name  = prev[ -1 ].split( '"' )[ 0 ]
                #- name += u'_inne'
                #- res  += u'Inne</label><label for="id_' + \
                        #- unicode( name ) + \
                        #- '"></label><input type="text" name="' + \
                        #- unicode( name ) + \
                        #- '" id="id_' + unicode( name ) + '" />' 
            #- else:
                #- res += entry
        #- 
        #- return SafeUnicode( res )
        #- 
