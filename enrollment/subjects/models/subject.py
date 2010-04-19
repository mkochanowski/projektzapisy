# -*- coding: utf8 -*-

from django.db import models
import re

class Subject( models.Model ):
    
    name = models.CharField(max_length=255, verbose_name='nazwa przedmiotu')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik')
    teachers = models.ManyToManyField('users.Employee', verbose_name='prowadzący')
    description = models.TextField(verbose_name='opis') 
    lectures = models.IntegerField(verbose_name='ilość godzin wykładów')
    exercises = models.IntegerField(verbose_name='ilość godzin ćwiczeń')
    laboratories = models.IntegerField(verbose_name='ilość godzin pracowni')
    
    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'subjects'
    
    def __str__(self):
        return unicode(self.name)
    
    def __unicode__(self):
        return self.name
        