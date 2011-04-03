# -*- coding: utf8 -*-

from django.db import models
from django.template.defaultfilters import slugify

from student_options import StudentOptions
from apps.enrollment.subjects.exceptions import NonStudentOptionsException

from datetime import timedelta, datetime

import logging
logger = logging.getLogger()

class SubjectEntity(models.Model):
    """entity of particular subject title"""
    name = models.CharField(max_length=100, verbose_name='nazwa')
    shortName = models.CharField(max_length=30, null=True, verbose_name='skrócona nazwa')

    class Meta:
        verbose_name = 'Podstawa przedmiotu'
        verbose_name_plural = 'Podstawy przedmiotów'
        app_label = 'subjects'
        
    def __unicode__(self):
        return '%s' % (self.name, )

    def get_short_name(self):
        if self.shortName is None:
            return self.name
        else:
            return self.shortName

class VisibleManager(models.Manager):
    """ Manager for subject objects with visible semester """
    def get_query_set(self):
        """ Returns all subjects which have marked semester as visible """
        return super(VisibleManager, self).get_query_set().filter(semester__visible=True)

class Subject( models.Model ):
    """subject in offer"""
    entity = models.ForeignKey(SubjectEntity, verbose_name='podstawa przedmiotu')
    name = models.CharField(max_length=255, verbose_name='nazwa przedmiotu')
    semester = models.ForeignKey('Semester', null=True, verbose_name='semestr')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik', null=True)
    type = models.ForeignKey('Type', null=True, verbose_name='rodzaj')
    teachers = models.ManyToManyField('users.Employee', verbose_name='prowadzący')
    description = models.TextField(verbose_name='opis') 
    lectures = models.IntegerField(verbose_name='wykład')
    exercises = models.IntegerField(verbose_name='ćwiczenia')
    laboratories = models.IntegerField(verbose_name='pracownia')
    students_options = models.ManyToManyField('users.Student', verbose_name='opcje studentów', through='StudentOptions')
    repetitions = models.IntegerField(verbose_name='Repetytorium', default=0)
    
    # XXX: fix tests (fixtures) to safely remove 'null=True' from semester field
    # and also fix get_semester_name method
    
    objects = models.Manager()
    visible = VisibleManager()
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify('%s %s' % (self.name, self.semester))
        super(Subject, self).save(*args, **kwargs)
        
    def is_recording_open_for_student(self, student):
        """ gives the answer to question: is subject opened for apps.enrollment for student at the very moment? """
        records_opening = self.semester.records_opening
        records_closing = self.semester.records_closing

        try:
            stud_opt = StudentOptions.get_student_options_for_subject(student.id, self.id)
            interval = stud_opt.get_opening_bonus_timedelta()
        except NonStudentOptionsException:
            interval = timedelta(minutes=0)

        if records_opening == None:
            return False
        else:
            if records_opening - interval < datetime.now():
                if records_closing == None:
                    return True
                else:
                    return datetime.now() < records_closing
            else:
                return False

    def get_enrollment_opening_time(self, student):
        """ returns apps.enrollment opening time as datetime object or None if apps.enrollment is opened / was opened """
        records_opening = self.semester.records_opening

        try:
            stud_opt = StudentOptions.get_student_options_for_subject(student.id, self.id)
            interval = stud_opt.get_opening_bonus_timedelta()
        except NonStudentOptionsException:
            interval = timedelta(minutes=0)

        if records_opening == None:
            return False
        else:
            if records_opening - interval < datetime.now():
                return None
            else:
                return records_opening - interval
    
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
        unique_together = (('name', 'semester'),)
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.get_semester_name())
		
