# -*- coding: utf8 -*-
from django.db                         import models
from fereol.users.models               import Employee, \
                                              Type
from fereol.enrollment.subjects.models import Group, \
                                                Subject, \
                                                Semester

class Poll( models.Model ):
    author       = models.ForeignKey( Employee, verbose_name = 'autor' )
    title        = models.CharField( max_length = 40, verbose_name = 'tytuł' )
    description  = models.TextField( blank = True, verbose_name = 'opis' )
    group        = models.ForeignKey( Group, verbose_name = 'grupa', blank = True, null = True )
    studies_type = models.ForeignKey( Type, verbose_name = 'typ studiów', blank = True, null = True )
    
    class Meta:
        verbose_name        = 'ankieta' 
        verbose_name_plural = 'ankiety'
        app_label           = 'poll'
        
    def __unicode__( self ):
        return u'[' + unicode( self.group ) + u']' + unicode( self.title )
        
    def is_student_entitled_to_poll( self, student ):
        pass
        
    def all_sections( self ):
        pass
    
    def get_semester( self ):
        pass
        
    @staticmethod
    def get_current_polls():
        pass
        
    @staticmethod
    def get_current_semester_polls():
        semester = Semester.get_current_semester()
        current_semester_subjects = Subject.objects.filter(semester = semester)
        current_semester_groups = Group.objects.filter(subject__in = current_semester_subjects)
        return Poll.objects.filter(group__in = current_semester_groups) 
