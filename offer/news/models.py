# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from datetime import datetime, timedelta

class NewsManager(models.Manager):
    def new(self):
        '''Zwraca ogłoszenia oznaczone jako nowe.'''
        if self.count_new() >= 3:
            begin = datetime.now() - timedelta(days=7)
            return self.filter(date__gte=begin)
        else:
           return self.get_successive_news(0, 3)
    def count_new(self):
        '''Zwraca liczbę ogłoszeń oznaczonych jako nowe.

        Zwraca liczbę ogłoszeń z ostatnich 7 dni.'''
        begin = datetime.now() - timedelta(days=7)
        return self.filter(date__gte=begin).count()
    def get_successive_news(self, beginwith, quantity=1):
        return News.objects.all()[beginwith:(beginwith+quantity)]

class News(models.Model):
    title = models.CharField(max_length=255,
                             verbose_name=u'Tytuł')
    body = models.TextField(verbose_name=u'Treść',
                            blank=True)
    date = models.DateTimeField(default=datetime.now)
    author = models.ForeignKey(User)
    
    objects = NewsManager()
    
    class Meta:
        get_latest_by = 'date'
        ordering = ['-date','-id']
        verbose_name = u'Ogłoszenie'
        verbose_name_plural = u'Ogłoszenia'
    
    def __unicode__(self):
        return self.title

    
