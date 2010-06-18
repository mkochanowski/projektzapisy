# -*- coding: utf8 -*-

from django.db import models

from student_options import StudentOptions
from enrollment.subjects.exceptions import NonStudentOptionsException

from datetime import timedelta, datetime

import logging
logger = logging.getLogger()

class SubjectEntity(models.Model):
    """entity of particular subject title"""
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name = 'Podstawa przedmiotu'
        verbose_name_plural = 'Podstawy przedmiotów'
        app_label = 'subjects'
        
    def __unicode__(self):
        return '%s' % (self.name, )
    

class VisibleManager(models.Manager):
    """ Manager for subject objects with visible semester """
    def get_query_set(self):
        """ Returns all subjects which have marked semester as visible """
        return super(VisibleManager, self).get_query_set().filter(semester__visible=True)

class Subject( models.Model ):
    """subject in offer"""
    entity = models.ForeignKey(SubjectEntity)
    name = models.CharField(max_length=255, verbose_name='nazwa przedmiotu')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik')
    semester = models.ForeignKey('Semester', null=True, verbose_name='semestr')
    type = models.ForeignKey('Type', null=True, verbose_name='rodzaj')
    ects = models.IntegerField(verbose_name="punkty ECTS", null=True)
    teachers = models.ManyToManyField('users.Employee', verbose_name='prowadzący')
    description = models.TextField(verbose_name='opis') 
    lectures = models.IntegerField(verbose_name='ilość godzin wykładów')
    exercises = models.IntegerField(verbose_name='ilość godzin ćwiczeń')
    laboratories = models.IntegerField(verbose_name='ilość godzin pracowni')
    students_options = models.ManyToManyField('users.Student', verbose_name='opcje studentów', through='StudentOptions')
    
    # XXX: fix tests (fixtures) to safely remove 'null=True' from semester field
    # and also fix get_semester_name method
    
    objects = models.Manager()
    visible = VisibleManager()
    
    def is_recording_open_for_student(self, student):
        """ gives the answer to question: is student enrolling open for this subject at the very moment? """
        records_opening = self.semester.records_opening
        records_closing = self.semester.records_closing

        if records_opening < datetime.now():
            if records_closing == None:
                return True
            else:
                return datetime.now() < records_closing
        else:
            return False

#       try:
#           stud_opt = StudentOptions.get_student_options_for_subject(student.id, self.id)
#           records_opening = self.semester.records_opening 
#           records_closing = self.semester.records_closing
#           if records_opening == None:
#               return False
#           else:
#               student_records_opening = records_opening + stud_opt.get_opening_delay_timedelta()
#               if student_records_opening < datetime.now():
#                   if records_closing == None:
#                       return True
#                   else:
#                       return datetime.now() < records_closing
#       except NonStudentOptionsException:
#           logger.info('Subject.is_recording_open_for_student(student = %s) throws NonStudentOptionsException exception.' % str(student) )
#           return False
                
    
    def get_semester_name(self):
        """ returns name of semester subject is linked to """
        if self.semester is None:
            logger.warning('Subject.get_semester_name() was invoked with non unknown semester.')
            return "nieznany semestr"
        else:
            return self.semester.get_name()
    
    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'subjects'
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.get_semester_name())
		
