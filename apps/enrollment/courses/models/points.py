# -*- coding: utf8 -*-

from django.db import models
     
class PointTypes(models.Model):
    """types of points"""
    name = models.CharField(max_length=30, verbose_name='rodzaj punktów', default="", unique=False)

    class Meta:
        verbose_name = 'rodzaj punktu'
        verbose_name_plural = 'rodzaje punktów'
        app_label = 'courses'

    def __unicode__(self):
        return '%s' % (self.name, )

class PointsOfCourseEntities(models.Model):
    entity = models.ForeignKey('CourseEntity', verbose_name='podstawa przedmiotu')
    type_of_point = models.ForeignKey('PointTypes', verbose_name='rodzaj punktów')
    value = models.PositiveSmallIntegerField(verbose_name='liczba punktów')

    class Meta:
        verbose_name = 'zależność podstawa przedmiotu-punkty'
        verbose_name_plural = 'zależności podstawy przedmiotu-punkty'
        app_label = 'courses'

    def __unicode__(self):
        return '%s: %s %s' % (self.entity.name, self.value, self.type_of_point)
    
class PointsOfCourses(models.Model):
    course = models.ForeignKey('Course', verbose_name='przedmiot')
    type_of_point = models.ForeignKey('PointTypes', verbose_name='rodzaj punktów')
    program = models.ForeignKey('users.Program', verbose_name='Program Studiów', null=True, blank=True, default=None)
    value = models.PositiveSmallIntegerField(verbose_name='liczba punktów')

    class Meta:
        verbose_name = 'zależność przedmiot-punkty'
        verbose_name_plural = 'zależności przedmiot-punkty'
        app_label = 'courses'

    def __unicode__(self):
        return '%s: %s %s' % (self.course.name, self.value, self.type_of_point)
