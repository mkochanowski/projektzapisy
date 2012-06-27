# -*- coding: utf8 -*-

from django.db import models
from course import Course
from django.core.exceptions import MultipleObjectsReturned
from apps.enrollment.courses.exceptions import *
from django.db.models import Q

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
    records_ects_limit_abolition = models.DateTimeField(null = True, verbose_name='Czas zniesienia limitu 40 ECTS') 

    def get_courses(self):
        """ gets all courses linked to semester """
        return Course.objects.filter(semester=self.pk)
		
    def get_name(self):
        """ returns name of semester """
        #TODO: wymuszanie formatu roku "XXXX/YY" zamiast "XXXX"
        if len(self.year) != 7:
            return '%s %s (BLAD)' % (self.get_type_display() , self.year)
        return '%s %s' % (self.year, self.get_type_display())

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
                return Semester.objects.filter(year=year,type='z')[0]
            except KeyError:
                return None
            except IndexError:
                return None
        else:
            prev_year = str(int(year[0:4])-1)
            year = prev_year+'/'+year[2:4]
            try:
                return Semester.objects.filter(year=year,type='l')[0]
            except KeyError:
                return None
            except IndexError:
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
        now = datetime.now()
        now_date = now.date()
        semesters = list(Semester.objects.filter(
            Q(semester_beginning__lte=now_date, semester_ending__gte= now_date) 
            | 
            Q(records_opening__lte=now, records_closing__gte=now)))

        if len(semesters)>1:
            semesters_with_open_records = [s for s in semesters if s.semester_beginning<=now_date and s.semester_ending<=now_date]
            if len(semesters_with_open_records)==1:
                return semesters_with_open_records[0]
            else:
                raise MoreThanOneSemesterWithOpenRecordsException() 
        elif len(semesters)==1:
            return semesters[0]
        else:
            next_semester = Semester.objects.filter(records_opening__gte =now).order_by('records_opening')
            if next_semester.exists():
                return next_semester[0]
            else:
                return None

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
