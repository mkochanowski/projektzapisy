# -*- coding: utf8 -*-

from django.db import models

     
class Type(models.Model):
    """types of subjects"""
    name = models.CharField(max_length=30, verbose_name='rodzaj zajec', default="", unique=False)
    group     = models.ForeignKey("self", null=True, blank=True, verbose_name='grupa')
    meta_type = models.BooleanField(default = False, verbose_name ='Grupa typow')
	#TODO: dodać unique na parę (meta_type, name)
    
    @staticmethod
    def get_all_types():
        return Type.objects.select_related('group').all()

    @staticmethod
    def get_all_for_jsfilter():
        return Type.objects.select_related('group').order_by('name').all()
    
    def get_name(self):
        self.name

    class Meta:
        verbose_name = 'rodzaj przedmiotu'
        verbose_name_plural = 'rodzaje przedmiotów'
        app_label = 'subjects'

    def __unicode__(self):
        return "%s" % (self.name)

    @staticmethod
    def get_types():
        """
            Zwraca wszystkie typy przedmiotów z wyjątkiem abstrakcyjnych
        """
        return Types.objects.filter(meta_type=False)
