# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import smart_unicode
from django.core.validators import ValidationError
from .term import Term

# this breaks the app - why?
# from apps.enrollment.courses.models import Semester, Term, Classroom

from apps.enrollment.courses.models import Semester

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


class FixedValidationError(ValidationError):
    def __init__(self, message, code=None, params=None):
        super(FixedValidationError, self).__init__(message, code, params)
        self.message_dict = dict()


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
    start_time = models.TimeField(verbose_name='rozpoczęcie', blank=False)
    end_time = models.TimeField(verbose_name='zakończenie', blank=False)

    objects = SpecialReservationManager()

    def validate_unique(self, *args, **kwargs):
        super(SpecialReservation, self).validate_unique(*args, **kwargs)

        overlaps = SpecialReservation.objects.\
            on_day_of_week(self.dayOfWeek).\
            in_classroom(self.classroom).\
            filter(start_time__lte=self.end_time).\
            filter(end_time__gte=self.start_time)

        if not self._state.adding and self.pk is not None:
            overlaps = overlaps.exclude(pk=self.pk)

        if overlaps:
            raise ValidationError(message={'classroom': ['Overlaps with another reservation: ' + smart_unicode(overlaps[0])]},
                                  code='overlap_special')

        # TODO: Learn to validate models

        # anything here breaks validation
        # candidate_days = self.semester.get_all_days_of_week(self.dayOfWeek)
        # overlaps = Term.get_conflicted(candidate_days, self.start_time, self.end_time)
        # if overlaps:
        #    print "ITS HAPPENING"
        #    raise ValidationError(message={'semester': ['Overlaps with event terms']},
        #                         code='overlap_event')

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
