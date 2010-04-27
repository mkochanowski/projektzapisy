# -*- coding: utf8 -*-

from django.db import models

class Subject( models.Model ):
    
    name = models.CharField(max_length=255, verbose_name='nazwa przedmiotu')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik')
    teachers = models.ManyToManyField('users.Employee', verbose_name='prowadzący')
    description = models.TextField(verbose_name='opis') 
    lectures = models.IntegerField(verbose_name='ilość godzin wykładów')
    exercises = models.IntegerField(verbose_name='ilość godzin ćwiczeń')
    laboratories = models.IntegerField(verbose_name='ilość godzin pracowni')
    semester = models.ForeignKey('Semester', null=True, verbose_name='semestr')
    
    # XXX: fix tests (fixtures) to safely remove 'null=True' from semester field
    # and also fix get_semester_name method
    
    def get_semester_name(self):
        if self.semester is None:
            return "nieznany semestr"
        else:
            return self.semester.get_name()
    
    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'subjects'
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.get_semester_name())
        