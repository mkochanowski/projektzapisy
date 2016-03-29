# -*- coding: utf-8 -*-
from django.db.models import Q
from django.db import models
from django.db.models.query import EmptyQuerySet
from timedelta import TimedeltaField
from datetime import time
from .event import Event

from django.utils.encoding import smart_unicode

class Term(models.Model):
    """
    Term representation
    """

    event = models.ForeignKey(Event, verbose_name=u'Wydarzenie')

    day = models.DateField(verbose_name=u'Dzień')

    start = TimedeltaField(verbose_name=u'Początek')
    end = TimedeltaField(verbose_name=u'Koniec')

    room = models.ForeignKey('courses.Classroom', null=True, blank=True, verbose_name=u'Sala',
                             related_name='event_terms')
    place = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'Miejsce')

    def validate_unique(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        from django.db.models import Q

        if self.room:
            terms = self.__class__.objects.filter(Q(room=self.room), Q(day=self.day), Q(event__status='1'),
                                                  Q(start__lt=self.end), Q(end__gt=self.start)).select_related('event')

            if self.pk:
                terms = terms.exclude(pk=self.pk)

            if terms.count():
                raise ValidationError({'__all__': (u'Ta sala w podanym terminie jest zajęta',)})

        super(self.__class__, self).validate_unique(*args, **kwargs)

    def clean(self):
        """
        Overloaded method from models.Model
        """
        from django.core.exceptions import ValidationError

        if self.start >= self.end:
            raise ValidationError(u'Koniec musi następować po początku.')

        if not self.room and not self.place:
            raise ValidationError(u'Musisz podać salę lub miejsce.')

    class Meta:
        app_label = 'schedule'
        get_latest_by = 'end'
        ordering = ['day', 'start', 'end']
        verbose_name = u'termin'
        verbose_name_plural = u'terminy'

    def get_conflicted(self):

        if not self.room:
            return EmptyQuerySet()

        # X < B AND A < Y

        terms = Term.objects.filter(Q(room=self.room), Q(day=self.day),
                                    Q(start__lt=self.end), Q(end__gt=self.start)) \
            .select_related('event')

        if self.pk:
            terms = terms.exclude(pk=self.pk)

        return terms

    def print_start(self):
        """
        Print beautfull time

        @return: string
        """

        hours, remainder = divmod(self.start.seconds, 3600)
        minutes, __ = divmod(remainder, 60)
        return '%d:%02d' % (hours, minutes)

    def print_end(self):
        """
        Print beautfull time

        @return: string
        """
        hours, remainder = divmod(self.end.seconds, 3600)
        minutes, __ = divmod(remainder, 60)
        return '%d:%02d' % (hours, minutes)

    @classmethod
    def get_exams(cls):
        """
        Get list of events with type 'exam'

        @return: Term QuerySet
        """
        return cls.objects.filter(event__type__in=['0', '1']).order_by('day', 'event__course__entity__name', 'room') \
            .select_related('event', 'room', 'event__course', 'event__course__entity', 'event__course__semester')

    @classmethod
    def get_terms_for_dates(cls, dates, classroom, start_time=None, end_time=None):
        """
        Gets terms in specified classroom on specified days

        :param end_time: datetime.time
        :param start_time: datetime.time
        :param classroom: enrollment.courses.models.Classroom
        :param dates: datetime.date list
        """
        if start_time is None:
            start_time = time(8)
        if end_time is None:
            end_time = time(21)

        terms = Term.objects.filter(day__in=dates,
                                    start__lt=end_time,
                                    end__gt=start_time,
                                    room=classroom,
                                    event__status=Event.STATUS_ACCEPTED).select_related('event')

        return terms

    def __unicode__(self):
        return '{0:s}: {1:s} - {2:s}'.format(smart_unicode(self.day),
                                             smart_unicode(self.start),
                                             smart_unicode(self.end))
