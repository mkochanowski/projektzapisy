# -*- coding: utf8 -*-

from datetime import time

from django.db import models
from django.db.models import signals
from django.core.cache import cache as mcache

import logging

backup_logger = logging.getLogger('project.backup')

DAYS_OF_WEEK = [( '1', 'poniedziałek' ), ( '2', 'wtorek' ), ( '3', 'środa' ), ( '4', 'czwartek'), ( '5', 'piątek'), ( '6', 'sobota'), ( '7', 'niedziela')]

HOURS = [(str(hour), "%s.00" % hour) for hour in range(8, 23)] 
  
class Term(models.Model):
    """terms of groups"""
    dayOfWeek = models.CharField( max_length = 1, choices = DAYS_OF_WEEK, verbose_name = 'dzień tygodnia') 
    start_time = models.TimeField(verbose_name = 'rozpoczęcie')
    end_time = models.TimeField(verbose_name = 'zakończenie')
    classroom = models.ForeignKey('Classroom', verbose_name='sala')
    group = models.ForeignKey('Group', verbose_name='grupa', related_name='term')
    classrooms = models.ManyToManyField('Classroom', related_name='new_classrooms', verbose_name='sale')

    class Meta:
        #TO DO /pkacprzak/ add advanced constraint - example: start_time < end_time, any pair of terms can't overlap
        verbose_name = 'termin'
        verbose_name_plural = 'terminy'
        ordering  = ['dayOfWeek']
        app_label = 'courses'
    
    
    @staticmethod
    def get_all_in_semester(semester, student=None, employee=None):
        filtered = Term.objects.filter(group__course__semester=semester)
        
        if student:
            from apps.enrollment.records.models import Record
            filtered = filtered.filter(group__id__in=\
                Record.get_student_enrolled_ids(student, semester))
                
        if employee:
            from apps.enrollment.records.models import Record
            filtered = filtered.filter(group__teacher=employee)
            
        return filtered.select_related('classroom', 'classrooms', 'group', 'group__course', \
            'group__course__semester', 'group__course__entity',
            'group__course__type', \
            'group__teacher', 'group__teacher__user').\
            order_by('dayOfWeek', 'start_time').all()

    def day_in_zero_base(self):
        return int(self.dayOfWeek)-1
    
    def length_in_minutes(self):
        return (self.end_time.hour - self.start_time.hour)*60 + (self.end_time.minute - self.start_time.minute)
    
    def time_from_in_minutes(self):
        "Returns number of minutes from start of day (midnight) to term beggining"""
        return (self.start_time.hour)* 60 + (self.start_time.minute) 

    def time_from(self):
        "Returns hourFrom in time format"""
        return self.start_time
  
    def time_to(self):
        "Returns hourTo in time format"""
        return self.end_time

    def _convert_string_to_time(self, str):
        hour, minute = map(lambda x: int(x), str.split('.'))
        return time(hour=hour, minute=minute)
    
    def period_string(self):
        return "%s – %s" % (self.start_time.strftime("%H"), self.end_time.strftime("%H"))
        
    def get_dayOfWeek_display_short(self):
        return { '1': 'pn', '2': 'wt', '3': 'śr', '4': 'cz', '5': 'pt', '6': 'so', '7': 'nd'}[self.dayOfWeek].decode('utf8')
    
    @staticmethod
    def get_groups_terms(groups_ids):
        """
        Optimized query returning terms as string for group ids.
        """
        return map(lambda x: {'group_id':x.group_id,'term_as_string': "%s %s-%s (s.%s)" % (x.get_dayOfWeek_display_short(), x.start_time.strftime("%H:%M"), x.end_time.strftime("%H:%M"), x.classrooms_as_string)},
                   Term.objects.filter(group__in=groups_ids).extra(select={'classrooms_as_string': """
                                    SELECT array_to_string(array(SELECT courses_classroom.number FROM courses_term_classrooms
                                    JOIN courses_classroom 
                                    ON (courses_classroom.id = courses_term_classrooms.classroom_id)
                                    WHERE courses_term.id=courses_term_classrooms.term_id),',')"""}))
    
    def __unicode__(self):
        """
        N query problem with self.classrooms.all(). If you want to optimize, use Term.get_groups_terms.
        """
        classrooms = self.classrooms.all()
        if len(classrooms) > 0:
            classrooms = ' (s.' + ', '.join(map(lambda x: x.number, self.classrooms.all())) + ')'
        else:
            classrooms = ''
        return "%s %s-%s%s" % (self.get_dayOfWeek_display_short(), self.start_time.strftime("%H:%M"), self.end_time.strftime("%H:%M"), classrooms)

def log_edit_term(sender, instance, **kwargs):
    try:
        term = instance
        old_term = Term.objects.get(id=term.id)
        old_term_format = '-'.join([old_term.dayOfWeek,str(old_term.start_time),str(old_term.end_time),old_term.classroom.number])
        term_format = '-'.join([term.dayOfWeek,str(term.start_time),str(term.end_time),term.classroom.number])
        message = '[09] term for group <%s> has been updated from <%s> to <%s>' % (term.group.id, old_term_format.encode('utf-8'), term_format.encode('utf-8')) 
        backup_logger.info(message)
    except Term.DoesNotExist:
        pass

def log_add_term(sender, instance, created, **kwargs):
    term = instance
    term_format = '-'.join([term.dayOfWeek,str(term.start_time),str(term.end_time),term.classroom.number])
    if created:
        message = '[08] term <%s> for group <%s> has been created' % (term_format.encode('utf-8'), term.group.id) 
        backup_logger.info(message)
        
def log_delete_term(sender, instance, **kwargs):
    term = instance
    term_format = '-'.join([term.dayOfWeek,str(term.start_time),str(term.end_time),term.classroom.number])
    backup_logger.info('[10] term <%s> for group <%s> has been deleted' % (term_format.encode('utf-8'), term.group.id))
            
signals.pre_save.connect(log_edit_term, sender=Term)          
signals.post_save.connect(log_add_term, sender=Term)                               
signals.pre_delete.connect(log_delete_term, sender=Term)  

def recache(sender, **kwargs):
    mcache.clear()
    
signals.post_save.connect(recache, sender=Term)        
signals.post_delete.connect(recache, sender=Term)	
