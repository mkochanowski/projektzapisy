# -*- coding: utf-8 -*-
from django                            import forms
from django.utils.safestring           import SafeUnicode

class PollCombineForm( forms.Form ):
    def __init__( self, *args, **kwargs ):
        polls_by_s       = kwargs.pop( "polls" )
        self.poll_groups = []
        
        super( PollCombineForm, self ).__init__( *args, **kwargs )
                
        for polls in polls_by_s:
            if len( polls ) == 1:
                if not polls[ 0 ].group:
                    title = u'[' + polls[ 0 ].title + u'] Ankieta ogólna'
                else:
                    title = u'[' + polls[ 0 ].title + u'] Przedmiot: ' + \
                            polls[ 0 ].group.subject.name + \
                            u' ' + polls[ 0 ].group.get_type_display() + u': ' + \
                            polls[ 0 ].group.get_teacher_full_name()
                if polls[ 0 ].studies_type: u', studia ' + polls[ 0 ].studies_type
                
                self.poll_groups.append( unicode( title ))
            else:
                if not polls[ 0 ].group:
                    title = u'Ankiety ogólne:<ul>'
                    label = u'join_common'
                else:
                    title = u'Przedmiot: ' + polls[ 0 ].group.subject.name + u'<ul>'
                    label = u'join_' + unicode( polls[ 0 ].group.subject.pk )
                for poll in polls:
                    if not poll.group:
                        title += u'<li>[' + poll.title + ']'
                    else:
                        title += u'<li>[' + poll.title + u'] ' + \
                                 poll.group.get_type_display() + u': ' + \
                                 poll.group.get_teacher_full_name()
                
                field = forms.BooleanField( label     = SafeUnicode( title ),
                                            required  = False,
                                            initial   = True,
                                            help_text = u'Powiąż ocenę' )
                
                self.fields[ label ] = field
                
    def as_table( self ):
        result  = u"<tr><th>Pobieranie biletów na następujące ankiety:</th></tr>"
        for name in self.poll_groups:
            result += u"<tr><th>" + unicode( name )+ u"</th></tr>"
        result += super( PollCombineForm, self ).as_table()
        return SafeUnicode( result )

class ContactForm(forms.Form):
    idUser = forms.CharField()
    passwordUser = forms.CharField()
    groupNumber = forms.CharField()
    groupKey = forms.CharField()

class GetKey(forms.Form):
    n = forms.CharField()
