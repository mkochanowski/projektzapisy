# -*- coding: utf8 -*-

from django.db import models

from enrollment.subjects.exceptions import NonStudentOptionsException

from datetime import timedelta, datetime

import logging
logger = logging.getLogger()

class StudentOptions( models.Model ):
    """ Used for defining time bonus in records - for Student, Subject. Student gets bonuses if voted for subject. """
    subject = models.ForeignKey('Subject', verbose_name = 'przedmiot')
    student = models.ForeignKey('users.Student', verbose_name = 'student')
    records_opening_delay_minutes = models.IntegerField(verbose_name='Przyspieszenie otwarcia zapisów na ten przedmiot (minuty)')

    def get_opening_bonus_timedelta(self):
        """ returns records opening bonus as timedelta """
        return timedelta(minutes=self.records_opening_delay_minutes)
    
    @staticmethod
    def get_student_options_for_subject(student_id, subject_id):
        """ returns StudentOption instance for student and subject id, throws NonStudentOptionsException if such record do not exist""" 
        try:    
            return StudentOptions.objects.get(subject__id=subject_id, student__id=student_id)
        except StudentOptions.DoesNotExist:
            logger.error('StudentOptions.get_student_options_for_subject(student_id = %d, subject_id = %d) throws StudentOptions.DoesNotExist exception.' % (int(student_id), int(subject_id)) )
            raise NonStudentOptionsException()
    
    class Meta:
        verbose_name = 'zależność przedmiot-student'
        verbose_name_plural = 'zależności przedmiot-student'
        unique_together = (('subject', 'student'),)
        app_label = 'subjects'

    def __unicode__(self):
        """ returns printable name of StudentOptions """
        return u'Przedmiot: %s, Student: %s ' % (self.subject, self.student)
