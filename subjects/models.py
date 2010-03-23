# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from fereol.users.models import Employee

class Subject( models.Model ):
    
    name = models.CharField( max_length = 255, verbose_name = 'nazwa przedmiotu' )
    slug = models.SlugField( max_length=255, unique = True, verbose_name='odnośnik' )
    description = models.TextField( verbose_name = 'opis' )
    lectures = models.IntegerField( verbose_name = 'ilość godzin wykładów' )
    exercises = models.IntegerField( verbose_name = 'ilość godzin ćwiczeń' )
    laboratories = models.IntegerField( verbose_name = 'ilość godzin pracownii' )
    
    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
    
    def __unicode__(self):
        return self.name

GROUP_TYPE_CHOICES = [ ( '1', u'wykład' ), ( '2', u'ćwiczenia' ), ( '3', u'pracownia' ) ]

def group_type(type):
    d = {}
    for x, y in GROUP_TYPE_CHOICES:
        d[x] = y
    return d[type] 

class Group( models.Model ):
    
    subject = models.ForeignKey( Subject, verbose_name = 'przedmiot' )
    teacher = models.ForeignKey( Employee, verbose_name = 'prowadzący' )
    type = models.CharField( max_length = 1, choices = GROUP_TYPE_CHOICES, verbose_name = 'typ zajęć' )
    
    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'
        
    def __unicode__(self):
        return self.subject.name + ': ' + group_type( self.type )
    
