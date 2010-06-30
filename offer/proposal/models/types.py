# -*- coding: utf8 -*-

"""
    Types of Lectures
"""

from django.db import models

class Types( models.Model ):
    """
       h Types of Lectures
    """
    
    name      = models.TextField( verbose_name='nazwa' )
    group     = models.ForeignKey("self", null=True, blank=True, verbose_name='grupa')
    meta_type = models.BooleanField(default = False, verbose_name ='Grupa typow')

    class Meta:
        """
            Django Class
        """
        verbose_name = 'Typ przedmiotu'
        verbose_name_plural = 'Typy przedmiotu'
        app_label = 'proposal'

    def __str__(self):
        """
            Djano method
        """
        return self.name

    def __unicode__(self):
        """
            Django method
        """
        return self.name

    @staticmethod
    def get_types():
        """
            Zwraca wszystkie typy przedmiotów z wyjątkiem abstrakcyjnych
        """
        return Types.objects.filter(meta_type=False)

