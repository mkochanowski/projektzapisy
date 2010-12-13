# -*- coding: utf-8 -*-
from django                            import forms
from django.utils.safestring           import SafeUnicode
from fereol.enrollment.subjects.models import Subject
################################################################################
##      TODO:                                                                 ##
##              Zdezaktywowanie już pobranych grup                            ##
################################################################################

class GroupChooseForm( forms.Form ):
    def __init__( self, *args, **kwargs ):
        groups     = kwargs.pop( 'subject_groups' )
        self.title = kwargs.pop( 'subject' )
        super( GroupChooseForm, self).__init__( *args, **kwargs )
    
        for i, group in enumerate( groups ):
            field = forms.BooleanField( label = unicode( "%s: %s" % ( group.get_type_display(), group.get_teacher_full_name())),
                                        required = False )
            self.fields[ unicode( Subject.objects.get( name = self.title ).pk ) + u'_' + unicode( group.pk ) + u'_' + unicode( i ) ] = field
    
    def as_table( self ):
        return SafeUnicode( u'<tr><th>' + unicode( self.title ) + u'</tr></th>' + super( GroupChooseForm, self ).as_table())
