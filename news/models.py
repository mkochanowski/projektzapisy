# -*- coding: utf-8 -*-

from django.db import models

from datetime import datetime, timedelta

class NewsManager(models.Manager):
    def new(self):
        '''Zwraca ogłoszenia oznaczone jako nowe.

        Zwraca ogłoszenia z ostatnich 7 dni.'''
        begin = datetime.now() - timedelta(days=7)
        return self.filter(date__gte=begin)
    def count_new(self):
        '''Zwraca liczbę ogłoszeń oznaczonych jako nowe.

        Zwraca liczbę ogłoszeń z ostatnich 7 dni.'''
        begin = datetime.now() - timedelta(days=7)
        return self.filter(date__gte=begin).count()


class News(models.Model):
    title = models.CharField(max_length=255,
                             verbose_name=u'Tytuł')
    body = models.TextField(verbose_name=u'Treść',
                            blank=True)
    date = models.DateTimeField(default=datetime.now)
    
    objects = NewsManager()
    
    class Meta:
        get_latest_by = 'date'
        ordering = ['-date','-id']
        verbose_name = 'ogłoszenie'
        verbose_name_plural = 'ogłoszenia'
    
    def __unicode__(self):
        return self.title
