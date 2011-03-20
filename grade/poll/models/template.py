# -*- coding: utf8 -*-
from django.db                         import models
from django.utils.safestring           import SafeUnicode

from fereol.users.models               import Employee, \
                                              Student, \
                                              Type
from fereol.enrollment.subjects.models import Group, \
                                              Subject, \
                                              Semester, \
                                              GROUP_TYPE_CHOICES
from fereol.enrollment.records.models  import Record, \
                                              STATUS_ENROLLED
from fereol.grade.ticket_create.models import PublicKey                                              
from section                           import SectionOrdering

class Template( models.Model ):
    title             = models.CharField( max_length = 40, verbose_name = 'tytuł' )
    description       = models.TextField( blank = True, verbose_name = 'opis' )
    studies_type      = models.ForeignKey( Type, verbose_name = 'typ studiów', blank = True, null = True )
    subject           = models.ForeignKey( Subject, verbose_name = 'przedmiot', blank = True, null = True)
    group_type        = models.CharField(max_length=1, choices=GROUP_TYPE_CHOICES, verbose_name='typ zajęć')
    share_result      = models.BooleanField( verbose_name = 'udostępnij wyniki', default = False, blank = True )
    deleted           = models.BooleanField( blank = False, null = False, default = False, verbose_name = 'usunięty' )
    
    class Meta:
        verbose_name        = 'szablon' 
        verbose_name_plural = 'szablony'
        app_label           = 'poll'
        ordering            =['title']
        
    def __unicode__( self ):
        res = unicode( self.title )
        if self.studies_type: res += u', typ studiów: ' + unicode( self.studies_type )
        if self.subject:      res += u', przedmiot: ' + unicode( self.subject )
        if self.group_type:   res += u', typ grupy: ' + unicode( self.group_type )
        return res
        
