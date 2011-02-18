# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from users.exceptions import NonEmployeeException, NonStudentException
from enrollment.subjects.models import Group, Semester

import datetime

from fereol import settings

import logging
logger = logging.getLogger()

class BaseUser(models.Model):
    '''
    User abstract class. For every app user there is entry in django.auth.
    We do not inherit after User directly, because of problems with logging beckend etc.
    '''
    user = models.OneToOneField(User)
    receive_mass_mail_enrollment = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia Zapisów")
    receive_mass_mail_offer = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia OD")
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    @staticmethod
    def get(user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error('Getter(user_id = %d) in BaseUser throws User.DoesNotExist exception.' % user_id )
            raise NonUserException
        return user
    
    class Meta:
        abstract = True

class Employee(BaseUser):
    '''
    Employee.
    '''
    consultations = models.TextField(verbose_name="konsultacje")
    
    @staticmethod
    def get_all_groups(user_id):
        user = User.objects.get(id=user_id)
        try:
            employee = user.employee
            groups = Group.objects.filter(teacher=employee)
        except Employee.DoesNotExist:
             logger.error('Function Employee.get_all_groups(user_id = %d) wthrows Employee.DoesNotExist exception.' % user_id )
             raise NonEmployeeException()
        return groups
    
    @staticmethod
    def get_schedule(user_id):
        user = User.objects.get(id=user_id)
        try:
            employee = user.employee
            groups = [g for g in Employee.get_all_groups(user_id) if g.subject.semester.is_current_semester()] 
            subjects = set([group.subject for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.subject_ = group.subject
            return groups
        except Employee.DoesNotExist:
             logger.error('Function Employee.get_schedule(user_id = %d) throws Employee.DoesNotExist exception.' % user_id )
             raise NonEmployeeException()
         
    class Meta:
        verbose_name = 'pracownik'
        verbose_name_plural = 'Pracownicy'
        app_label = 'users'
      
    def __unicode__(self):
        return str(self.user)

class Student(BaseUser):
    ''' 
    Student.
    '''
    matricula = models.CharField(max_length=20, default="", unique=True, verbose_name="Numer indeksu")
    ects = models.PositiveIntegerField(verbose_name="punkty ECTS", default=0)
    records_opening_delay_minutes = models.PositiveIntegerField(default=0, verbose_name="Opóźnienie w otwarciu zapisów (minuty)")
    type = models.ForeignKey('Type', null=True, blank=True, verbose_name='Typ Studiów')
    block = models.BooleanField(verbose_name="blokada planu", default = False)

    def get_t0_interval(self):
        return datetime.timedelta(minutes=(self.records_opening_delay_minutes + self.ects * settings.ECTS_BONUS)) #TODO: Sprawdzić, czy student brał udział w ocenie zajęć, jezeli tak - dodać datetime.timedelta(days=1) -- poprawić przy merge'owaniu z oceną...

    def get_records_history(self):
        '''
        Returns list of ids of subject s that student was enrolled for.
        '''
        default_semester = Semester.get_default_semester()
        records = self.records.exclude(group__subject__semester = default_semester)
        records_list = map(lambda x: x.group.subject.entity.id, records)
        return list(frozenset(records_list))
    
    @staticmethod
    def get_all_groups(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            groups = map(lambda x: x.group, student.records.filter(status="1"))
        except Student.DoesNotExist:
             logger.error('Function Student.get_all_groups(user_id = %d) throws Student.DoesNotExist exception.' % user_id )
             raise NonStudentException()
        return groups
    
    @staticmethod
    def get_schedule(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            groups = [g for g in Student.get_all_groups(user_id) if g.subject.semester.is_current_semester()]
            subjects = set([group.subject for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.subject_ = group.subject
            return groups
        except Student.DoesNotExist:
             logger.error('Function Student.get_schedule(user_id = %d) throws Student.DoesNotExist exception.' % user_id )
             raise NonStudentException()
         
    @staticmethod
    def records_block(user_id):
        user = User.objects.get(id=user_id)
        try :
            student = user.student
            if student.block == False:
                student.block = True
                student.save()
                return student
            else :
                return False
        except Student.DoesNotExist:
             logger.error('Function Student.records_block(user_id = %d) throws Student.DoesNotExist exception.' % user_id )
             raise NonStudentException()
    @staticmethod
    def records_unblock(user_id):
        user = User.objects.get(id=user_id)
        try :
            student = user.student
            if student.block == True:
                student.block = False
                student.save()
                return student
            else :
                return False
        except Student.DoesNotExist:
             logger.error('Function Student.records_unblock(user_id = %d) throws Student.DoesNotExist exception.' % user_id )
             raise NonStudentException()
         
    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'studenci'
        app_label = 'users'
    
    def __unicode__(self):
        return str(self.user)

class Type( models.Model ):
    """
        Model przechowuje informacje o typie studiow
    """
    name = models.CharField(max_length=30, unique=True, verbose_name="Typ")

    class Meta:
        """
            Klasa django
        """
        verbose_name = 'Typ studiów'
        verbose_name_plural = 'Typy studiów'

    def __unicode__(self):
        """
            metoda django
        """
        return self.name

    @staticmethod
    def get_types():
        """
            Typy studiow
        """
        return Type.objects.all()
