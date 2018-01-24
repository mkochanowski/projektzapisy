# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class TermSyncData(models.Model):
    """Models the relation between """
    term = models.ForeignKey('courses.Term', verbose_name='termin')
    scheduler_id = models.PositiveIntegerField(null=True, unique=True,
                                               verbose_name='id grupy w schedulerze')

    class Meta:
        verbose_name = 'Obiekt synchronizacji terminów grup'
        verbose_name_plural = 'Obiekty synchronizacji terminów grup'
        app_label = 'schedulersync'
