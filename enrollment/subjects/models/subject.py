# -*- coding: utf8 -*-

from django.db import models

class SubjectEntity(models.Model):
    """entity of particular subject title"""
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name = 'encja przedmiotu'
        verbose_name_plural = 'encje przedmiotów'
        app_label = 'subjects'
        
    def __unicode__(self):
        return '%s' % (self.name, )
    

class VisibleManager(models.Manager):
    def get_query_set(self):
	    """ Returns all subjects which have marked semester as visible """
	    return super(VisibleManager, self).get_query_set().filter(semester__visible=True)

class Subject( models.Model ):
    """subject in offer"""
    entity = models.ForeignKey(SubjectEntity)
    name = models.CharField(max_length=255, verbose_name='nazwa przedmiotu')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik')
    semester = models.ForeignKey('Semester', null=True, verbose_name='semestr')
    type = models.ForeignKey('Type', null=True, verbose_name='rodzaj')
    teachers = models.ManyToManyField('users.Employee', verbose_name='prowadzący')
    description = models.TextField(verbose_name='opis') 
    lectures = models.IntegerField(verbose_name='ilość godzin wykładów')
    exercises = models.IntegerField(verbose_name='ilość godzin ćwiczeń')
    laboratories = models.IntegerField(verbose_name='ilość godzin pracowni')
    
    # XXX: fix tests (fixtures) to safely remove 'null=True' from semester field
    # and also fix get_semester_name method
    
    objects = models.Manager()
    visible = VisibleManager()
    
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
		
		
# TODO: move class to one another file 		
class Type(models.Model):
    """types of subjects"""
    name = models.CharField(max_length=30, verbose_name='rodzaj zajęć', default="", unique=True)
	
	
    @staticmethod
    def get_all_types_of_subjects():
        Type.objects.all()
    
    def get_name(self):
        self.name

    class Meta:
        verbose_name = 'rodzaj'
        verbose_name_plural = 'rodzaje'
        app_label = 'subjects'

    def __unicode__(self):
        return "%s" % (self.name)