# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class BaseUser(models.Model):
    '''
    User abstract class. For every app user there is entry in django.auth.
    We do not inherit after User directly, because of problems with logging beckend etc.
    '''
    user = models.OneToOneField(User)
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
    receive_mass_mail_offer = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia OD")
    
    class Meta:
        app_label = 'users'
        
    def __unicode__(self):
        return str(self.user)

class Student(BaseUser):
    ''' 
    Student.
    '''
    matricula = models.CharField(max_length=20, default="", unique=True, verbose_name="Numer indeksu")
    records_opening_delay_hours = models.PositiveIntegerField(default=0, verbose_name="Opóźnienie w otwarciu zapisów (godziny)")
    
    def __unicode__(self):
        return str(self.user)
