# -*- coding: utf8 -*-
from django.db                         import models
from django.utils.safestring           import SafeUnicode

from fereol.users.models               import Employee, \
                                              Type
from fereol.enrollment.subjects.models import Group, \
                                              Subject, \
                                              Semester
from fereol.enrollment.records.models  import Record, \
                                              STATUS_ENROLLED
from fereol.grade.ticket_create.models import PublicKey                                              
from section                           import SectionOrdering


class Poll( models.Model ):
    author       = models.ForeignKey( Employee, verbose_name = 'autor' )
    title        = models.CharField( max_length = 40, verbose_name = 'tytuł' )
    description  = models.TextField( blank = True, verbose_name = 'opis' )
    semester     = models.ForeignKey( Semester, verbose_name = 'semestr' )
    group        = models.ForeignKey( Group, verbose_name = 'grupa', blank = True, null = True )
    studies_type = models.ForeignKey( Type, verbose_name = 'typ studiów', blank = True, null = True )
    
    class Meta:
        verbose_name        = 'ankieta' 
        verbose_name_plural = 'ankiety'
        app_label           = 'poll'
        
    def __unicode__( self ):
        res = unicode( self.title )
        if self.group: res += u', grupa: ' + unicode( self.group )
        if self.studies_type: res += u', typ studiów: ' + unicode( self.studies_type )
        return res
        
    def is_student_entitled_to_poll( self, student ):
        if self.group:
            rec = Record.objects.filter( student = student, 
                                         group   = self.group,
                                         status  = STATUS_ENROLLED )
            try:                
                rec[ 0 ]
            except:
                return False
                
        if self.studies_type:
            if self.studies_type != student.type:
                return False
        
        return True 
               
    def all_sections( self ):
        return self.section_set.all()
    
    def as_row( self ):
        res  = u"<tr><td>"
        res += unicode( self.pk ) + u'</td><td>'
        res += unicode( self.title ) + u'</td><td>'
        
        if self.group:
            res += unicode( self.group.subject.name ) + u'</td><td>'
            res += unicode( self.group.get_type_display()) + u'</td><td>'
            res += unicode( self.group.get_teacher_full_name()) + u'</td><td>'
        else:
            res += u'-</td><td>-</td><td>-</td><td>'
        
        if self.studies_type:
            res += unicode( self.studies_type ) + u'</td><td>'
        else:
            res += u'-</td><td>'
            
        res += unicode( " &#10;".join(PublicKey.objects.get( poll = self.pk ).public_key.split('\n')))
        res += u'</td></tr>'
        return SafeUnicode( res )
        
    @staticmethod
    def get_current_polls():
        pks = PublicKey.objects.all() 
        return Poll.objects.filter( pk__in = pks )
        
    @staticmethod
    def get_current_semester_polls_without_keys():
        semester = Semester.get_current_semester()
        polls_with_keys = PublicKey.objects.all().values_list( 'poll' )
        return Poll.objects.filter( semester = semester ).exclude( pk__in = polls_with_keys)        

    @staticmethod
    def get_all_polls_for_student( student ):
        return filter( lambda x: x.is_student_entitled_to_poll( student ), 
                       Poll.get_current_polls())
    
