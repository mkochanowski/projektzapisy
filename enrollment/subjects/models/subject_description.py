# -*- coding: utf8 -*-

from django.db import models

class SubjectDescription(models.Model):
    """description of particular subject"""
    subject = models.ForeignKey('Subject', related_name = 'descriptions')
    description = models.TextField( verbose_name = 'opis' )
    date = models.DateTimeField(verbose_name = 'data dodania')

    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotu'
        app_label = 'subjects'

    def __str__(self):
        return self.description

    def __unicode__(self):
        return self.description