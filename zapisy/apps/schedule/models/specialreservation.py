# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import smart_unicode
from django.core.validators import ValidationError

from apps.enrollment.courses.models import Semester, Term as CourseTerm

from .term import Term


class SpecialReservationQuerySet(models.query.QuerySet):
    def on_day_of_week(self, day_of_week):
        return self.filter(dayOfWeek=day_of_week)

    def this_semester(self):
        return self.filter(semester=Semester.get_current_semester())

    def any_semester(self, semester):
        return self.filter(semester=semester)

    def in_classroom(self, classroom):
        return self.filter(classroom=classroom)

    def in_classrooms(self, classrooms):
        return self.filter(classroom__in=classrooms)

    def between_hours(self, start_time, end_time):
        return self.filter(start_time__lt=end_time, end_time__gt=start_time)


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

    def between_hours(self, start_time, end_time):
        return self.get_query_set().between_hours(start_time, end_time)


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

    @classmethod
    def get_reservations_for_semester(cls, semester=None, day_of_week=None):
        """Gets special reservations for a semester and day of the week

        :param semester: enrollment.courses.model.Semester
        :param day_of_week: Term.DAYS_OF_WEEK
        """

        if semester is None:
            semester = Semester.get_current_semester()

        query = cls.objects.any_semester(semester)
        if day_of_week is None:
            return query
        else:
            return query.on_day_of_week(day_of_week)

    def clean(self):
        """
        Overloaded clean method. Checks for any conflicts between this SpecialReservation
        and other SpecialReservations, Terms of Events and Terms of Course Groups

        """

        if not self.classroom.can_reserve:
            raise ValidationError(
                message={'classroom': ['This classroom is not available for reservation']},
                code='invalid'
            )

        # Fetch conflicting SpecialReservations

        overlaps = SpecialReservation.objects. \
            on_day_of_week(self.dayOfWeek). \
            in_classroom(self.classroom). \
            between_hours(self.start_time, self.end_time).\
            any_semester(self.semester)

        if not self._state.adding and self.pk is not None:
            overlaps = overlaps.exclude(pk=self.pk)

        if overlaps:
            raise ValidationError(
                message={'__all__': ['Overlaps with another reservation: ' + unicode(overlaps[0])]},
                code='overlap_special')

        # Fetch conflicting Events

        candidate_days = self.semester.get_all_days_of_week(self.dayOfWeek)
        overlaps = Term.get_terms_for_dates(dates=candidate_days,
                                            classroom=self.classroom,
                                            start_time=self.start_time,
                                            end_time=self.end_time)

        if overlaps:
            raise ValidationError(message={'__all__': ['Overlaps with a term for event ' + unicode(overlaps[0].event) +
                                                       ' ' + unicode(overlaps[0])]},
                                  code='overlap_event')

        # Fetch conflicting Course Terms
        # TODO: Test this part

        overlaps = CourseTerm.objects.filter(dayOfWeek=self.dayOfWeek,
                                             group__course__semester=self.semester,
                                             classrooms=self.classroom,
                                             start_time__lt=self.end_time,
                                             end_time__gt=self.start_time).select_related('group__course')

        if overlaps:
            raise ValidationError(
                message={'__all__': ['Overlaps with a group term for course ' + overlaps[0].group.course.name +
                                     ' ' + unicode(overlaps[0])]},
                code='overlap_course'
            )

        super(SpecialReservation, self).clean()

    def save(self, **kwargs):
        """Validate model before saving"""
        self.full_clean()
        super(SpecialReservation, self).save(kwargs)

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
