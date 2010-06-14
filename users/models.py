# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from users.exceptions import NonEmployeeException
from enrollment.subjects.models import Group

class BaseUser(models.Model):
    '''
    User abstract class. For every app user there is entry in django.auth.
    We do not inherit after User directly, because of problems with logging beckend etc.
    '''
    user = models.OneToOneField(User)
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    @staticmethod
    def get(user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NonUserException
        return user
    
    class Meta:
        abstract = True

class Employee(BaseUser):
    '''
    Employee.
    '''
    consultations = models.TextField(verbose_name="konsultacje")
    receive_mass_mail_offer = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia OD")
    
    @staticmethod
    def get_all_groups(user_id):
        user = User.objects.get(id=user_id)
        try:
            employee = user.employee
            groups = Group.objects.filter(teacher=employee)
        except Employee.DoesNotExist:
             raise NonEmployeeException()
        return groups
    
    @staticmethod
    def get_schedule(user_id):
        user = User.objects.get(id=user_id)
        try:
            employee = user.employee
            groups = Employee.get_all_groups(user_id)
            subjects = set([group.subject for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.subject_ = group.subject
            return groups
        except Employee.DoesNotExist:
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
    records_opening_delay_hours = models.PositiveIntegerField(default=0, verbose_name="Opóźnienie w otwarciu zapisów (godziny)")
    receive_mass_mail_offer = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia OD")
    
    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'studenci'
        app_label = 'users'
    
    def __unicode__(self):
        return str(self.user)
