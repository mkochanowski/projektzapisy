# -*- coding: utf8 -*-

from datetime import datetime
from django.db import models
from subject import Subject

from datetime import datetime

class Semester( models.Model ):
    """semester in academic year"""
    TYPE_WINTER = 'z'
    TYPE_SUMMER = 'l'
    TYPE_CHOICES = [(TYPE_WINTER, u'zimowy'), (TYPE_SUMMER, u'letni')]

    visible = models.BooleanField(verbose_name='widoczny')
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, verbose_name='rodzaj semestru')
    year = models.CharField(max_length=7, default='0', verbose_name='rok akademicki')
    records_opening = models.DateTimeField(blank = True, null = True, verbose_name='Czas otwarcia zapisów')
    records_closing = models.DateTimeField(blank = True, null = True, verbose_name='Czas zamkniecia zapisów')
    semester_begining = models.DateField(blank = True, null = False, verbose_name='Data rozpoczęcia semestru')
    semester_ending = models.DateField(blank = True, null = False, verbose_name='Data zakończenia semestru')

    def get_subjects(self):
        """ gets all subjects linked to semester """
        return Subject.objects.filter(semester=self.pk)
		
    def get_name(self):
        """ returns name of semester """
        return '%s %s' % (self.get_type_display() , self.year)

    def is_current_semester(self):
        """ Answers to question: is semester current semester""" 
        if self.semester_begining==None or self.semester_ending==None:
            return False
        return (self.semester_begining <= datetime.now().date() and self.semester_ending >= datetime.now().date())
    
    @staticmethod
    def get_current_semester():
        """ returns current semester """ 
        return Semester.objects.get(semester_begining__lt =datetime.now().date(), semester_ending__gt= datetime.now().date())

    @staticmethod
    def is_visible(id):
        """ Answers if subject is sat as visible (displayed on subject lists) """
        param = id
        return Semester.objects.get(id = param).visible 

    class Meta:
        verbose_name = 'semestr'
        verbose_name_plural = 'semestry'
        app_label = 'subjects'
        unique_together = (('type', 'year'),)
        ordering = ['-year', 'type']

    def __unicode__(self):
        return self.get_name()
