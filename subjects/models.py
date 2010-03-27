# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from fereol.users.models import Employee

class Subject( models.Model ):
    
    name = models.CharField( max_length = 255, verbose_name = 'nazwa przedmiotu' )
    slug = models.SlugField( max_length=255, unique = True, verbose_name='odnośnik' )
    #description = models.TextField( verbose_name = 'opis' ) # description should be in other model (for history)
    lectures = models.IntegerField( verbose_name = 'iloś godzin wykładów' )
    exercises = models.IntegerField( verbose_name = 'ilość godzin ćwiczeń' )
    laboratories = models.IntegerField( verbose_name = 'ilość godzin pracownii' )
    
    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
    
    def description(self):
        """
            Get last description.
        """
        if self.descriptions.count() > 0:
            return self.descriptions.order_by('-date')[0]
        else:
            return None

    def __unicode__(self):
        return self.name

class SubjectDescription(models.Model):
    subject = models.ForeignKey(Subject, related_name = 'descriptions')
    description = models.TextField( verbose_name = 'opis' )
    date = models.DateTimeField(verbose_name = 'data dodania')

    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotu'

    def __str__(self):
        return self.description

    def __unicode__(self):
        return self.description

GROUP_TYPE_CHOICES = [ ( '1', u'wykład' ), ( '2', u'ćwiczenia' ), ( '3', u'pracownia' ) ]

def group_type(type):
    d = {}
    for x, y in GROUP_TYPE_CHOICES:
        d[x] = y
    return d[type]

class Classroom( models.Model ):
    
    number = models.CharField( max_length = 4, verbose_name = 'numer sali' )
    
    class Meta:
        verbose_name = 'sala'
        verbose_name_plural = 'sale'
    
    def __unicode__(self):
        return self.number
    
class Group( models.Model ):
    
    subject = models.ForeignKey( Subject, verbose_name = 'przedmiot' )
    teacher = models.ForeignKey( Employee, verbose_name = 'prowadzący' )
    type = models.CharField( max_length = 1, choices = GROUP_TYPE_CHOICES, verbose_name = 'typ zajęć' )
    classroom = models.ManyToManyField( Classroom, verbose_name = 'sala', related_name = 'grupy' )
    
    def get_teacher_full_name(self):
        return self.teacher.user.get_full_name()
    
    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'

    def __unicode__(self):
        return self.subject.name + ': ' + group_type( self.type )

class Books( models.Model ):
    subject = models.ForeignKey(Subject, verbose_name = 'przedmiot')
    name = models.TextField( verbose_name = 'nazwa' )
    
    class Meta:
        verbose_name = 'ksiazka'
        verbose_name_plural = 'ksiazki'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
