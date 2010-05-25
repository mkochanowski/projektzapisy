# -*- coding: utf8 -*-

from django.db import models

from datetime import timedelta
           
class StudentOptions( models.Model ):
    subject = models.ForeignKey('Subject', verbose_name = 'przedmiot')
    student = models.ForeignKey('users.Student', verbose_name = 'student')
    records_opening_delay_hours = models.IntegerField(verbose_name='opuźnienie w otwarciu zapisów (godziny)')

    def get_opening_delay_timedelta(self):
        return timedelta(seconds=60*60*opening_delay_hours)
    
    def get_opening_delay_hours(self):
        return opening_delay_hours

    def get_name(self):
        return 'Przedmiot: %s, Student: %s ' % (subject, student)
    
    class Meta:
        verbose_name = 'zależność przedmiot-student'
        verbose_name_plural = 'zależności przedmiot-student'
        unique_together = (('subject', 'student'),)
        app_label = 'subjects'

    def __unicode__(self):
        return self.get_name()