# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import smart_unicode


# this breaks the app - why?
# from apps.enrollment.courses.models import Semester, Term, Classroom


class SpecialReservationQuerySet(models.query.QuerySet):
    def on_day_of_week(self, day_of_week):
        return self.filter(dayOfWeek=day_of_week)

    def this_semester(self):
        from apps.enrollment.courses.models import Semester
        return self.filter(semester=Semester.get_current_semester())

    def any_semester(self, semester):
        return self.filter(semester=semester)

    def in_classroom(self, classroom):
        return self.filter(classroom=classroom)

    def in_classrooms(self, classrooms):
        return self.filter(classroom__in=classrooms)


class SpecialReservationManager(models.Manager):
    def get_query_set(self):
        return SpecialReservationQuerySet(self.model, using=self._db)

    def on_day_of_week(self, day_of_week):
        return self.get_query_set().on_day_of_week(day_of_week)

    def this_semester(self):
        return self.get_query_set().this_semester()

    def any_semester(self, semester):
        return self.get_query_set().any_semester(semester)

    def in_classroom(self, classroom):
        return self.get_query_set().in_classroom(classroom)

    def in_classrooms(self, classrooms):
        return self.get_query_set().in_classrooms(classrooms)


class SpecialReservation(models.Model):
    from apps.enrollment.courses.models import Semester, Term, Classroom

    semester = models.ForeignKey(Semester)
    title = models.CharField(max_length=255)
    classroom = models.ForeignKey(Classroom)
    dayOfWeek = models.CharField(max_length=1,
                                 choices=Term.DAYS_OF_WEEK,
                                 verbose_name='dzień tygodnia')
    start_time = models.TimeField(verbose_name='rozpoczęcie')
    end_time = models.TimeField(verbose_name='zakończenie')

    objects = SpecialReservationManager()

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
