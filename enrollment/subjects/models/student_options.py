# -*- coding: utf8 -*-

from django.db import models

from enrollment.subjects.exceptions import NonStudentOptionsException

from datetime import timedelta, datetime

import logging
logger = logging.getLogger()

class StudentOptions( models.Model ):
    """ Used for defining relation between Student and Subject """
    subject = models.ForeignKey('Subject', verbose_name = 'przedmiot')
    student = models.ForeignKey('users.Student', verbose_name = 'student')
    records_opening_delay_hours = models.IntegerField(verbose_name='opóźnienie w otwarciu zapisu (godziny)')

    def get_opening_delay_timedelta(self):
        """ returns records opening delay as timedelta """
        return timedelta(hours=self.get_opening_delay_hours())
    
    def get_opening_delay_hours(self):
        """ returns records opening delay as imteger standing for hours """
        student_records_opening_delay_hours = self.student.records_opening_delay_hours
        return student_records_opening_delay_hours + self.records_opening_delay_hours
    
    @staticmethod
    def get_student_options_for_subject(student_id, subject_id):
        """ returns StudentOption instance for student and subject id, throws NonStudentOptionsException if such record do not exist""" 
        try:    
            return StudentOptions.objects.get(subject__id=subject_id, student__id=student_id)
        except StudentOptions.DoesNotExist:
            logger.error('StudentOptions.get_student_options_for_subject(student_id = %d, subject_id = %d) throws StudentOptions.DoesNotExist exception.' % (int(student_id), int(subject_id)) )
            raise NonStudentOptionsException()


    def get_name(self):
        """ gets printable name of StudentOptions """
        return u'Przedmiot: %s, Student: %s ' % (self.subject, self.student)
    
    class Meta:
        verbose_name = 'zależność przedmiot-student'
        verbose_name_plural = 'zależności przedmiot-student'
        unique_together = (('subject', 'student'),)
        app_label = 'subjects'

    def __unicode__(self):
        return self.get_name()