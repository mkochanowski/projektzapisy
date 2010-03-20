from django.db import models
from django.contrib.auth.models import User

class BaseUser(models.Model):
    '''
    Abstrakcyjna klasa uzytkownika. Dla kazdego uzytkownika aplikacji mamy wpis w django.auth.
    
    Nie dziedziczymy po User bezposrednio, bo jest ogolnie zamieszanie z calym backendem logowania itp.
    '''
    user = models.OneToOneField(User)
    
    class Meta:
        abstract = True

class Employee(BaseUser):
    '''
    Pracownik.
    '''
    
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
