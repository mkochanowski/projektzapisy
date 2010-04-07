# -*- coding: utf8 -*-

from django.db import models

class Subject( models.Model ):
    
    name = models.CharField( max_length = 255, verbose_name = 'nazwa przedmiotu' )
    slug = models.SlugField( max_length=255, unique = True, verbose_name='odnośnik' )
    #description = models.TextField( verbose_name = 'opis' ) # description should be in other model (for history)
    lectures = models.IntegerField( verbose_name = 'ilość godzin wykładów' )
    exercises = models.IntegerField( verbose_name = 'ilość godzin ćwiczeń' )
    laboratories = models.IntegerField( verbose_name = 'ilość godzin pracowni' )
    
    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'subjects'
    
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