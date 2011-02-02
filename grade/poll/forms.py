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

from fereol.grade.poll.models import Section, OpenQuestionAnswer, \
                                     SingleChoiceQuestionAnswer, \
                                     MultipleChoiceQuestionAnswer


from fereol.enrollment.subjects.models      import Semester

class TicketsForm( forms.Form ):
    ticketsfield = forms.CharField( widget = forms.widgets.Textarea( 
                                                    attrs = {'cols' : 80, 
                                                             'rows' : 20 }), 
                                 label     = "Podaj wygenerowane bilety",
                                 help_text = "Wklej tutaj pobrane wcześniej bilety." )

class PollForm( forms.Form ):
    class myObject:
        pass
    
    #- wydzielic do forma Section
    def as_edit(self):
        from django.template import loader
        return loader.render_to_string('grade/poll/section_as_edit.html', {"sections": self.sections})
            
    def as_divs(self):
        from django.template import loader
        return loader.render_to_string('grade/poll/poll_show.html', {"sections": self.sections})
    
    def setFields( self, poll = None, st = None, section_id = None ):
    	if st:
        	self.finished = st.finished
        else:
        	self.finished = True

        if poll:
            ppk = poll.pk
        else:
            ppk = 0
            
        self.sections = []
        
        if section_id:
            sections_set = []
            sections_set.append( Section.objects.get(pk = section_id) )
        elif poll:
            sections_set = poll.all_sections()
        else:
            section_set = {}
        
        for section in sections_set:
            title     = 'poll-%d_section-%d' % ( ppk, section.pk )
            questions = section.all_questions()
            fields    = []
            poll_section             = self.myObject()
            poll_section.title       = section.title
            poll_section.description = section.description
            poll_section.questions   = []
            if str( type( questions[ 0 ])) == \
                "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestion'>":
                questionOrdering  = SingleChoiceQuestionOrdering.objects.get( 
                        sections = section,
                        question = questions[ 0 ])
               
                if questionOrdering.is_leading:
                    title   += '_question-%d-leading' % questions[ 0 ].pk
                    try:
                        answer = SingleChoiceQuestionAnswer.objects.get( 
                                    saved_ticket = st,
                                    section      = section,
                                    question     = questions[ 0 ] ).option.pk
                    except ObjectDoesNotExist:
                        answer = None
                    
                    choices = []
                    for option in questions[ 0 ].options.all().order_by('pk'):
                        choices.append(( option.pk, unicode( option.content )))
                    
                    field = forms.ChoiceField( 
                                choices  = choices,
                                label    = unicode( questions[ 0 ].content ),
                                required = False,
                                widget   = forms.widgets.RadioSelect(),
                                initial  = answer )
                    
                    field.is_leading = True
                    field.hide_on    = map(lambda x: x.pk, questionOrdering.hide_on.all())
                    field.title      = title
                    #field.is_scale   = question.is_scale
                    field.type       = u'single'
                    if self.finished: field.widget.attrs[ 'disabled' ] = True
                    poll_section.questions.append( field )
                    
                    if self.finished: field.disabled = True
                    self.fields[ unicode( title ) ] = field
                    questions = questions[ 1: ]
                    
            for question in questions:
                title = 'poll-%d_section-%d_question-%d' % ( ppk, section.pk, question.pk )
                if str( type( question )) == \
                    "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestion'>":
                    title += '-single'
                    
                    if question.is_scale:
                        title += '-scale'

                    try:
                        answer = SingleChoiceQuestionAnswer.objects.get( 
                                    saved_ticket = st,
                                    section      = section,
                                    question     = question ).option.pk
                    except ObjectDoesNotExist:
                        answer = None
                        
                    choices = []
                    for option in question.options.all().order_by('pk'):
                        choices.append(( option.pk, unicode( option.content )))
                    
                    field = forms.ChoiceField( choices  = choices,
                                               label    = unicode( question.content ),
                                               required = False,
                                               widget   = forms.widgets.RadioSelect(),
                                               initial  = answer )
                    field.type = 'single'
                    if question.is_scale: field.is_scale  = True
                    if self.finished: field.widget.attrs[ 'disabled' ] = True
                    field.title        = title
                    if self.finished: field.disabled = True
                    poll_section.questions.append( field )
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
                    for option in question.options.all().order_by('pk'):
                        choices.append(( option.pk, unicode( option.content )))
                    
                    if question.has_other:
                        choices.append(( -1, unicode( 'Inne' )))
                        other_field = forms.CharField( 
                                        label    = u'', 
                                        initial  = other_ans,
                                        required = False )
                        if self.finished: other_field.widget.attrs[ 'disabled' ] = True
                        if other_ans: answer.append( -1 )
                    
                    field = forms.MultipleChoiceField( 
                                choices    = choices,
                                label      = unicode( question.content ),
                                required   = False,
                                widget     = forms.widgets.CheckboxSelectMultiple(),
                                initial    = answer,
                                validators = [ MaxLengthValidator( question.choice_limit )])
                    field.choice_limit     = question.choice_limit 
                    field.has_other        = question.has_other
                    field.type             = 'multi'
                    field.title = title 
                    if self.finished: field.disabled = True
                    if question.has_other:
                        field.other = other_field
                    poll_section.questions.append( field )
                    self.fields[ unicode( title ) ] = field
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
                    if self.finished: field.widget.attrs[ 'disabled' ] = True
                    field.type    =  'open'
                    field.title = title
                    if self.finished: field.disabled = True
                    poll_section.questions.append( field )
                    self.fields[ unicode( title ) ] = field
            self.sections.append(poll_section)
        if not self.finished:
            field = forms.BooleanField(
                            label     = u'Zakończ oceniać',
                            required  = False,
                            initial   = False,
                            help_text = u'Jeśli zaznaczysz to pole, utracisz mozliwość edycji ankiety po zapisaniu.' )
            self.finish = field
            self.fields[ u'finish' ] = field


class FilterMenu( forms.Form ):
    
    sem = Semester.objects.all()
    
    li = []
    
    for s in  sem:
        li.append(s.year)
        
    li.sort()
    
    li = list(set(li))
    
    begin = []
    end = []
    
    for l in li:
        begin.append((l,l))
        end.append((l,l))

    semestr_date_begin  =   forms.ChoiceField( label = 'od', choices = begin )
    semestr_date_end    =   forms.ChoiceField( label = 'do', choices = begin )

    semestr_winter      =   forms.BooleanField( label = 'zimowy' )    
    semestr_summer      =   forms.BooleanField( label = 'letni' )

    own_resource        =   forms.BooleanField( label = 'własne' )
    available_resource  =   forms.BooleanField( label = 'udostępnione' )
    
    lecture             =   forms.BooleanField( label = 'wykłady' )
    tutorial            =   forms.BooleanField( label = 'ćwiczenia' )
    lab                 =   forms.BooleanField( label = 'pracownie')

    order               =   forms.TypedChoiceField( widget=forms.RadioSelect, choices=((1,"wg nazwisk prowadzących"),(2,"wg nazw przedmiotów")))

    special             =   forms.BooleanField()
        
    
    
