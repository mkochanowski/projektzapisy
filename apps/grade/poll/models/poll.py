# -*- coding: utf8 -*-
from django.db                         import models
from django.utils.safestring           import SafeUnicode

from apps.users.models               import Employee, \
                                              Student, \
                                              Type
from apps.enrollment.subjects.models import Group, \
                                              Subject, \
                                              Semester, \
                                              GROUP_TYPE_CHOICES
from apps.enrollment.records.models  import Record, \
                                              STATUS_ENROLLED
from apps.grade.ticket_create.models import PublicKey                                              
from section                           import SectionOrdering

class Poll( models.Model ):
    author            = models.ForeignKey( Employee, verbose_name = 'autor', related_name = 'author' )
    title             = models.CharField( max_length = 40, verbose_name = 'tytuł' )
    description       = models.TextField( blank = True, verbose_name = 'opis' )
    semester          = models.ForeignKey( Semester, verbose_name = 'semestr' )
    group             = models.ForeignKey( Group, verbose_name = 'grupa', blank = True, null = True )
    studies_type      = models.ForeignKey( Type, verbose_name = 'typ studiów', blank = True, null = True )
    share_result      = models.BooleanField( verbose_name = 'udostępnij wyniki', default = False, blank = True )
    deleted           = models.BooleanField( blank = False, null = False, default = False, verbose_name = 'usunięta' )
    
    class Meta:
        verbose_name        = 'ankieta' 
        verbose_name_plural = 'ankiety'
        app_label           = 'poll'
        ordering            = ['group__subject__name']
        
    def __unicode__( self ):
        res = unicode( self.title )
        if self.group: res += u', grupa: ' + unicode( self.group )
        if self.studies_type: res += u', typ studiów: ' + unicode( self.studies_type )
        return res
        
    def to_url_title( self, break_lines = False ):
        res = unicode( self.title )
        if break_lines:
            sep = u'<br>'
        else:
            sep = u', '
            
        if self.group: 
            res += sep + self.group.subject.name
            res += sep + self.group.get_type_display()
            res += u': '   + self.group.get_teacher_full_name()
        else:
            res += sep + u'Ankieta ogólna'
            
        if self.studies_type: 
            res += sep + u'typ studiów: ' + unicode( self.studies_type )
        
        return SafeUnicode( res )
        
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
    
    def is_user_entitled_to_view_result( self, user ):
        if not user.is_authenticated(): return False
        if user.is_superuser: return True
        if self.share_result: return True
        
        try:
            viewer  = user.employee
            
            if self.group:
                if viewer == self.group.teacher: return True
                
                lecture = filter( lambda (x,y): y == 'wykład', GROUP_TYPE_CHOICES )[ 0 ][ 0 ]
                groups  = Group.objects.filter( subject = self.group.subject, 
                                                teacher = viewer,
                                                type    = lecture )
                if groups: return True
            else:
                # Zakładam, że wszyscy pracownicy powinni widzieć wyniki ankiet
                # ogólnych
                return True
        except Employee.DoesNotExist: 
            pass
        
        return False
               
    def all_sections( self ):
        return self.section_set.all()
    
    def all_answers( self ):
        result = []
        for section in self.all_sections():
            result.append( section.all_answers( self ))
        return result
    
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
    def get_polls_for_semester( semester = None):
        if not semester:
            semester = Semester.get_current_semester()
        return Poll.objects.filter( semester = semester, deleted = False )
    
    @staticmethod
    def get_groups_without_poll():
        semester = Semester.get_current_semester()
        polls    = Poll.objects.filter( semester = semester, group__isnull=False, deleted = False ).order_by('pk') 
        polls    = map( lambda p: p.group_id, polls)
        groups   = Group.objects.filter(subject__semester = semester).order_by('pk')
        return filter( lambda g: g.pk not in polls, groups)
    
    @staticmethod
    def get_current_polls():
        pks = map( lambda (x,): x, PublicKey.objects.all().values_list( 'poll' ))
        return Poll.objects.filter( pk__in = pks, deleted=False )
        
    @staticmethod
    def get_current_semester_polls_without_keys():
        semester = Semester.get_current_semester()
        polls_with_keys = PublicKey.objects.all().values_list( 'poll' )
        return Poll.objects.filter( semester = semester, deleted=False ).exclude( pk__in = polls_with_keys)        

    @staticmethod
    def get_all_polls_for_student( student ):
        return filter( lambda x: x.is_student_entitled_to_poll( student ), 
                       Poll.get_current_polls())
    
    @staticmethod
    def get_all_polls_for_group( group ):
        semester = Semester.get_current_semester()
        return Poll.objects.filter( semester = semester, group = group, deleted=False )
    
    def get_section_by_id(self, section_id):
        return self.section_set.get(section__pk = section_id)
