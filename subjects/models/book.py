# -*- coding: utf8 -*-

from django.db import models

class Books( models.Model ):
    subject = models.ForeignKey('Subject', verbose_name = 'przedmiot')
    name = models.TextField( verbose_name = 'nazwa' )
    
    class Meta:
        verbose_name = 'książka'
        verbose_name_plural = 'książki'
        app_label = 'subjects'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
