# -*- coding: utf8 -*-

from django.db import models

     
class Type(models.Model):
    """types of subjects"""
    name = models.CharField(max_length=30, verbose_name='rodzaj zajec', default="", unique=True)
    
    
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