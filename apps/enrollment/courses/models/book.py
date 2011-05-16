# -*- coding: utf8 -*-

from django.db import models

class Book( models.Model ):
    """book useful to learn concrete course"""
    course = models.ForeignKey('Course', verbose_name = 'przedmiot', related_name = 'books')
    name = models.TextField( verbose_name = 'nazwa' )
    
    class Meta:
        verbose_name = 'książka'
        verbose_name_plural = 'książki'
        app_label = 'courses'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
