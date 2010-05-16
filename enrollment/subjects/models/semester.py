# -*- coding: utf8 -*-

from datetime import datetime
from django.db import models
from subject import Subject

class Semester( models.Model ):
    """semester in academic year"""
    TYPE_WINTER = 'z'
    TYPE_SUMMER = 'l'
    TYPE_CHOICES = [(TYPE_WINTER, u'zimowy'), (TYPE_SUMMER, u'letni')]

    visible = models.BooleanField(verbose_name='widoczny')
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, verbose_name='rodzaj semestru')
    year = models.PositiveIntegerField(default=lambda: datetime.now().year, verbose_name='rok akademicki')
    # implies academic year: year/(year+1)

    def get_subjects(self):
        return Subject.objects.filter(semester=self.pk)
		
    def get_name(self):
        return '%s %i/%i' % (self.get_type_display() , self.year, self.year + 1)

    @staticmethod
    def is_visible(id):
        param = id
        return Semester.objects.get(id = param).visible 

    class Meta:
        verbose_name = 'semestr'
        verbose_name_plural = 'semestry'
        app_label = 'subjects'
        unique_together = (('type', 'year'),)

    def __unicode__(self):
        return self.get_name()
