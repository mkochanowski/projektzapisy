# -*- coding: utf8 -*-

from django.db import models
from django.contrib.auth.models import User

class BaseUser(models.Model):
    '''
    User abstract class. For every app user there is entry in django.auth.
    We do not inherit after User directly, because of problems with logging beckend etc.
    '''
    user = models.OneToOneField(User)
    
    class Meta:
        abstract = True

class Employee(BaseUser):
    '''
    Employee.
    '''
    class Meta:
        app_label = 'users'
        
    def __unicode__(self):
        return str(self.user)

class Student(BaseUser):
    ''' 
    Student.
    '''
    def __unicode__(self):
        return str(self.user)
    
# tutsj oczywiscie bedziemy dodawac pola wg uznania
# widok w adminie rowniez do zaprojektownia (na podstawie w/w pol)
