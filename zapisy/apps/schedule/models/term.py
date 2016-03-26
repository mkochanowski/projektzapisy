# -*- coding: utf-8 -*-
from django.db.models import Q
from django.db import models
from django.db.models.query import EmptyQuerySet
from timedelta import TimedeltaField


class Term(models.Model):
    """
    Term representation
    """
    from apps.schedule.models import Event

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
    def get_conflicts_on_dates(cls, dates, start_time, end_time):
        return cls.objects.filter(day__in=dates,
                                  start_time__lt=end_time,
                                  end_time__gt=start_time)
