# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import smart_unicode


class SpecialReservation(models.Model):
    from apps.enrollment.courses.models import Semester, DAYS_OF_WEEK, Classroom

    semester = models.ForeignKey(Semester)
    title = models.CharField(max_length=255)
    classroom = models.ForeignKey(Classroom)
    dayOfWeek = models.CharField(max_length=1,
                                 choices=DAYS_OF_WEEK,
                                 verbose_name='dzień tygodnia')
    start_time = models.TimeField(verbose_name='rozpoczęcie')
    end_time = models.TimeField(verbose_name='zakończenie')

    class Meta:
        app_label = 'schedule'
        verbose_name = u'rezerwacja stała'
        verbose_name_plural = u'rezerwacje stałe'

    def __unicode__(self):
        return '{0:s}: {1:s} - {2:s} {3:s} - {4:s}'.format(smart_unicode(self.semester),
                                                           smart_unicode(self.title),
                                                           smart_unicode(self.get_dayOfWeek_display()),
                                                           smart_unicode(self.start_time),
                                                           smart_unicode(self.end_time))
