# -*- coding: utf-8 -*-
import datetime
from django.core.urlresolvers import reverse
from django.db.models import Q
from timedelta import TimedeltaField
import json

__author__ = 'maciek'


from django.db import models

types = [('0', u'Egzamin'), ('1', u'Kolokwium'), ('2', u'Wydarzenie'), ('3', u'Zajęcia')]
types_for_student = [('2', u'Wydarzenie')]
types_for_teacher = [('0', u'Egzamin'), ('1', u'Kolokwium'), ('2', u'Wydarzenie')]

statuses = [('0', u'Do rozpatrzenia'), ('1', u'Zaakceptowane'), ('2', u'Odrzucone')]
class Event(models.Model):
    """
    Model of Event
    """
    title       = models.CharField(max_length=255, verbose_name=u'Tytuł', null=True, blank=True)
    description = models.TextField(verbose_name=u'Opis')
    type        = models.CharField(choices=types, max_length=1, verbose_name=u'Typ')
    visible     = models.BooleanField(verbose_name=u'Wydarzenie jest publiczne')

    status      = models.CharField(choices=statuses, max_length=1, verbose_name=u'Stan', default='0')
    message     = models.TextField(null=True, blank=True, verbose_name=u'Wiadomość do moderatora')
    decision    = models.TextField(null=True, blank=True)

    course      = models.ForeignKey('courses.Course', null=True, blank=True)

    author      = models.ForeignKey('auth.User', verbose_name=u'Twórca')
    created     = models.DateTimeField(auto_now_add=True)
    edited      = models.DateTimeField(auto_now=True)

    def set_user(self, user):
        self.author = user

    def save(self, *args, **kwargs):
        if self.author.employee and self.type in ['0','1']:
            self.status = '1'
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:event_show', args=[str(self.id)])



    class Meta:
        verbose_name = u'wydarzenie'
        verbose_name_plural = u'wydarzenia'
        permissions = (
            ("manage_events", u"Może zarządzać wydarzeniami"),
        )

    @classmethod
    def get_from_request(cls, request=None):
        return cls.objects.all().select_related('course', 'author').prefetch_related('term_set')

    @classmethod
    def get_in_semester(cls, semester):
        return cls.objects.filter(course__semester=semester, status='1', type='0').select_related('course', 'course__entity')

    @classmethod
    def get_for_user(cls, user):
        return cls.objects.filter(author=user).select_related('course', 'author').prefetch_related('term_set')

class Term(models.Model):
    """
    Term representation
    """
    event = models.ForeignKey(Event, verbose_name=u'Wydarzenie')

    day = models.DateField(verbose_name=u'Dzień')

    start = TimedeltaField(verbose_name=u'Początek')
    end   = TimedeltaField(verbose_name=u'Koniec')

    room   = models.ForeignKey('courses.Classroom', null=True, blank=True, verbose_name=u'Sala', related_name='event_terms')
    place  = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'Miejsce')

    def clean(self):
        """
        Overloaded method from models.Model
        """
        from django.core.exceptions import ValidationError
        if self.start >= self.end:
            raise ValidationError(u'Koniec musi następować po początku.')

        if not self.room and not self.place:
            raise ValidationError(u'Musisz podać salę lub miejsce.')

#    def validate_unique(self, *args, **kwargs):
#        from django.core.exceptions import ValidationError
#        super(Term, self).validate_unique(*args, **kwargs)
#
#        qs = self.__class__.objects.filter(
#                    (Q(start__lte=self.end, end__gte=self.end) | Q(end__gte=self.start, end__lte=self.end)), Q(event__status='1')
#                )
#
#        if qs.exists():
#            raise ValidationError(u'Sala w tym terminie jest niedostępna.')


    class Meta:
        get_latest_by = 'end'
        ordering = ['start', 'end']
        verbose_name = u'termin'
        verbose_name_plural = u'terminy'


    @classmethod
    def get_exams(cls):
        return cls.objects.filter(event__type='0').order_by('day')

    @classmethod
    def get_week(cls, room, date):
        next_week = date + datetime.timedelta(days=6)
        return cls.objects.filter(room=room, day__range=(date, next_week)).select_related('event', 'event__course')



