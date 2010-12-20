# -*- coding: utf-8 -*-
from django                            import forms
from django.utils.safestring           import SafeUnicode
from fereol.enrollment.subjects.models import Subject

class GroupCombineForm( forms.Form ):
    def __init__( self, *args, **kwargs ):
        groups_by_s   = kwargs.pop( "groups_by_subject" )
        self.subjects = []
        
        super( GroupCombineForm, self ).__init__( *args, **kwargs )
        
        for groups in groups_by_s:
            if len( groups ) == 1:
                self.subjects.append( SafeUnicode( 
                            groups[ 0 ].subject.name + "<br>" + \
                            group.get_type_display() + ": " + \
                            group.get_teacher_full_name()))
            else:
                sub_key = Subject.objects.get( name = groups[ 0 ].subject.name).pk
                label   = "Przedmiot: " + groups[ 0 ].subject.name 
                for group in groups:
                    label += '<br>' + group.get_type_display() + ": " + \
                             group.get_teacher_full_name()
                field = forms.BooleanField( label    = SafeUnicode( label ),
                                            required = False,
                                            initial  = True,
                                            help_text = "Powiąż ocenę" )
                                            
                self.fields[ 'connect_' + unicode( sub_key ) ] = field 
                
    def as_table( self ):
        result  = u"<tr><th>Pobieranie biletów na ocenę następujących przedmiotów:</th></tr>"
        for sub in self.subjects:
            result += u"<tr><th>Przedmiot: " + unicode( sub )+ u"</th></tr>"
        result += super( GroupCombineForm, self ).as_table()
        return SafeUnicode( result )
