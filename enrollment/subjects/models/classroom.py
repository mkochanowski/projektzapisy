# -*- coding: utf8 -*-

from django.db import models

class Classroom( models.Model ):
    """classroom in institute"""
    number = models.CharField( max_length = 4, verbose_name = 'numer sali' )
    building = models.CharField( max_length = 50, verbose_name = 'budynek', blank=True, default='' )
    capacity = models.PositiveSmallIntegerField(default=0, verbose_name='liczba miejsc')   
    
    class Meta:
        verbose_name = 'sala'
        verbose_name_plural = 'sale'
        app_label = 'subjects'
    
    def __unicode__(self):
        return self.number
