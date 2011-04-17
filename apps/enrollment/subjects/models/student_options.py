# -*- coding: utf8 -*-

from django.db import models

from datetime import timedelta

import logging
logger = logging.getLogger()

class StudentOptions( models.Model ):
    """ Used for defining time bonus in records - for Student, Subject. Student gets bonuses if voted for subject. """
    subject = models.ForeignKey('Subject', verbose_name = 'przedmiot')
    student = models.ForeignKey('users.Student', verbose_name = 'student')
    records_opening_delay_minutes = models.IntegerField(verbose_name='Przyspieszenie otwarcia zapisów na ten przedmiot (minuty)')

    options_cache = {}

    @staticmethod
    def preload_cache(student, semester):
        '''
            Preloads cache with subjects for certain student and semester.
        '''
        if not student.id in StudentOptions.options_cache:
            StudentOptions.options_cache[student.id] = {}
        if not semester.id in StudentOptions.options_cache[student.id]:
            StudentOptions.options_cache[student.id][semester.id] = {}
        for option in StudentOptions.objects.filter(subject__semester=semester,\
            student=student).all():
            StudentOptions.options_cache[student.id][semester.id]\
                [option.subject.id] = option

    @staticmethod
    def get_cached(student, subject):
        '''
            Returns StudentOption instance for student and subject id.
            Doesn't make new query, if record is already cached.
        '''
        cache = StudentOptions.options_cache
        if not student.id in cache:
            cache[student.id] = {}
        if not subject.semester.id in cache[student.id]: # miss
            return StudentOptions.objects.get(subject=subject, student=student)
        if subject.id in cache[student.id][subject.semester.id]: # get
            return cache[student.id][subject.semester.id][subject.id]
        else: # not miss, but doesn't exists
            raise StudentOptions.DoesNotExist()

    def get_opening_bonus_timedelta(self):
        """ returns records opening bonus as timedelta """
        return timedelta(minutes=self.records_opening_delay_minutes)

    class Meta:
        verbose_name = 'zależność przedmiot-student'
        verbose_name_plural = 'zależności przedmiot-student'
        unique_together = (('subject', 'student'),)
        app_label = 'subjects'

    def __unicode__(self):
        """ returns printable name of StudentOptions """
        return u'Przedmiot: %s, Student: %s ' % (self.subject, self.student)
