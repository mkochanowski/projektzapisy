# -*- coding: utf8 -*-
from django.db import models


class Tag(models.Model):
    short_name = models.CharField(max_length=50, verbose_name=u'nazwa skrócona')
    full_name = models.CharField(max_length=250, verbose_name=u'nazwa pełna')
    description = models.TextField(verbose_name=u'opis')

    class Meta:
        verbose_name = u'Tag'
        verbose_name_plural = u'Tagi'
        app_label = 'courses'

    def __unicode__(self):
        return str(self.short_name) + ' (' + str(self.full_name) + ')'

