# -*- coding: utf8 -*-

from django.db import models
from course import Course
from django.core.exceptions import MultipleObjectsReturned
from apps.enrollment.courses.exceptions import *

from datetime import datetime

class Semester( models.Model ):
    """semester in academic year"""
    TYPE_WINTER = 'z'
    TYPE_SUMMER = 'l'
    TYPE_CHOICES = [(TYPE_WINTER, u'zimowy'), (TYPE_SUMMER, u'letni')]

    visible = models.BooleanField(verbose_name='widoczny')
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, verbose_name='rodzaj semestru')
    year = models.CharField(max_length=7, default='0', verbose_name='rok akademicki')
    records_opening = models.DateTimeField(null = True, verbose_name='Czas otwarcia zapisów', help_text='Godzina powinna być ustawiona na 00:00:00, by studenci mieli otwarcie między 10:00 a 22:00.') 
    records_closing = models.DateTimeField(null = True, verbose_name='Czas zamkniecia zapisów')
    semester_beginning = models.DateField(null = False, verbose_name='Data rozpoczęcia semestru')
    semester_ending = models.DateField(null = False, verbose_name='Data zakończenia semestru')

    is_grade_active = models.BooleanField( verbose_name = 'Ocena aktywna' )

    def get_courses(self):
        """ gets all courses linked to semester """
        return Course.objects.filter(semester=self.pk)
		
    def get_name(self):
        """ returns name of semester """
        return '%s %s' % (self.get_type_display() , self.year)

    def is_current_semester(self):
        """ Answers to question: is semester current semester""" 
        if self.semester_beginning == None or self.semester_ending == None:
            return False
        return (self.semester_beginning <= datetime.now().date() and self.semester_ending >= datetime.now().date())

    def get_previous_semester(self):
        """ returns previous semester """
        year = self.year
        if self.type=='l':
            try:
                Semester.objects.filter(year=year,type='z')[0]
            except KeyError:
                return None
        else:
            prev_year = (int(year[0:4])-1)
            year = prev_year+'/'+year[2:4]
            try:
                Semester.objects.filter(year=year,type='l')[0]
            except KeyError:
                return None
                
                
    @staticmethod
    def get_current_semester():
        """ if exist, it returns current semester. otherwise return None """ 
        try:
            return Semester.objects.get(semester_beginning__lte =datetime.now().date(), semester_ending__gte= datetime.now().date())
        except Semester.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise MoreThanOneCurrentSemesterException()  

    @staticmethod
    def get_default_semester():
        """Jeżeli istnieje semestr na który zapisy są otwarte, zwracany jest ten semestr, jeżeli taki nie istnieje zwracany jest semestr, który obecnie trwa. W przypadku gdy nie trwa żaden semestr, zwracany jest najbliższy semestr na który będzie można się zapisać lub None w przypadku braku takiego semestru """ 
        try:
            return Semester.objects.get(records_opening__lte =datetime.now(), records_closing__gte= datetime.now())
        except Semester.DoesNotExist:
            current_semester = Semester.get_current_semester()
            if current_semester:
                return current_semester
            else:
                next_semester = Semester.objects.filter(records_opening__gte =datetime.now()).order_by('records_opening')
                if next_semester.exists():
                    return next_semester[0]
                else:
                    return None
                        
        except MultipleObjectsReturned:
            raise MoreThanOneSemesterWithOpenRecordsException()  

    @staticmethod
    def is_visible(id):
        """ Answers if course is sat as visible (displayed on course lists) """
        param = id
        return Semester.objects.get(id = param).visible 


    class Meta:
        verbose_name = 'semestr'
        verbose_name_plural = 'semestry'
        app_label = 'courses'
        unique_together = (('type', 'year'),)
        ordering = ['-year', 'type']

    def __unicode__(self):
        return self.get_name()
