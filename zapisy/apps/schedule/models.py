# -*- coding: utf-8 -*-
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from timedelta import TimedeltaField
import json

__author__ = 'maciek'


from django.db import models

types = [('0', u'Egzamin'), ('1', u'Kolokwium'), ('2', u'Wydarzenie'), ('3', u'Zajęcia'), ('4', u'Inne')]
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

    course      = models.ForeignKey('courses.Course', null=True, blank=True)
    group       = models.ForeignKey('courses.Group',  null=True, blank=True)

    interested  = models.ManyToManyField('auth.User', related_name='interested_events')

    author      = models.ForeignKey('auth.User', verbose_name=u'Twórca')
    created     = models.DateTimeField(auto_now_add=True)
    edited      = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        """
        Overload save method.
        If author is employee and try reserve room for exam - accept it
        If author has perms to manage events - accept it
        """
        if not self.pk:
            if (self.author.employee and self.type in ['0','1']) or \
                self.author.has_perm('schedule.manage_events'):
                self.status = '1'

            if self.type in ['0','1']:
                self.visible = True

        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.group:
            return reverse('records-group', args=[self.group_id])
        return reverse('events:show', args=[str(self.id)])

    class Meta:
        verbose_name = u'wydarzenie'
        verbose_name_plural = u'wydarzenia'
        permissions = (
            ("manage_events", u"Może zarządzać wydarzeniami"),
        )

    def _user_can_see_or_404(self, user):
        """

        Private method. Return True if user can see event, otherwise False.

        @param user: auth.User
        @return: Boolean
        """
        if not self.author == user and not user.has_perm('schedule.manage_events'):
            if not self.visible or not self.type in ['0', '1', '2'] or self.status <> '1':
                return False

        return True

    @classmethod
    def get_event_or_404(cls, id, user):
        """

        If events exist and user can see it - return
        otherwise raise Http404

        @param id: Integer Number
        @param user:  auth.User
        @return: Event object
        """
        try:
            event = cls.objects.select_related('group', 'course', 'course__entity', 'author')\
                                     .prefetch_related('term_set', 'term_set__room').get(pk=id)
        except ObjectDoesNotExist:
            raise Http404

        if event._user_can_see_or_404(user):
            return event
        else:
            raise Http404

    @classmethod
    def get_event_for_moderation_or_404(cls, id, user):
        """

        If events exist and user can send moderation message - return it
        otherwise raise Http404

        @param id: Integer Number
        @param user:  auth.User
        @return: Event object
        """
        try:
            event = cls.objects.select_related('group', 'course', 'course__entity', 'author')\
                                     .prefetch_related('term_set', 'term_set__room').get(pk=id)
        except ObjectDoesNotExist:
            raise Http404

        if event.author == user or user.has_perm('schedule.manage_events'):
            return event
        else:
            raise Http404

    @classmethod
    def get_event_for_moderation_only_or_404(cls, id, user):
        """

        If events exist and user can send moderation message - return it
        otherwise raise Http404

        @param id: Integer Number
        @param user:  auth.User
        @return: Event object
        """
        try:
            event = cls.objects.select_related('group', 'course', 'course__entity', 'author')\
                                     .prefetch_related('term_set', 'term_set__room').get(pk=id)
        except ObjectDoesNotExist:
            raise Http404


        if user.has_perm('schedule.manage_events'):
            return event
        else:
            raise Http404

    @classmethod
    def get_all(cls):
        """

        Return all events with all needed select_related and prefetch_related

        @return: Event QuerySet
        """
        return cls.objects.all().select_related('group', 'course', 'course__entity', 'author')\
                                 .prefetch_related('term_set', 'term_set__room')

    @classmethod
    def get_for_user(cls, user):
        """
        Get list of events, where user is author

        @param user: auth.User object
        @return: Event QuerySet
        """
        return cls.objects.filter(author=user).select_related('course', 'course__entity', 'author').prefetch_related('term_set')

    @classmethod
    def get_exams(cls):
        """
        Return list of all exam

        @return Event QuerySet
        """
        return cls.objects.filter(type='0', status='1').order_by('-created')

    @classmethod
    def get_events(cls):
        """
        """

        return cls.objects.filter(status='1', type='0').order_by('-created')

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

    class Meta:
        get_latest_by = 'end'
        ordering = ['day', 'start', 'end']
        verbose_name = u'termin'
        verbose_name_plural = u'terminy'


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
        return cls.objects.filter(event__type='0').order_by('day')


class EventModerationMessage(models.Model):
    author  = models.ForeignKey('auth.User', verbose_name=u'Autor')
    event   = models.ForeignKey(Event, verbose_name=u'Wydarzenie')
    message = models.TextField(verbose_name=u'Wiadomość')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by ='created'
        ordering = ['created']
        verbose_name = u'wiadomość wydarzenia'
        verbose_name_plural = u'wiadomości wydarzenia'


    @classmethod
    def get_event_messages(cls, event):
        """

        Get list of EventMessages for event

        @param event: Event object
        @return: list of EventModerationMessage
        """

        return cls.objects.filter(event=event).select_related('author')


class Message(models.Model):
    author  = models.ForeignKey('auth.User', verbose_name=u'Autor')
    event   = models.ForeignKey(Event, verbose_name=u'Wydarzenie')
    message = models.TextField(verbose_name=u'Wiadomość')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by ='created'
        ordering = ['created']
        abstract = True


    @classmethod
    def get_event_messages(cls, event):
        """

        Get list of EventMessages for event

        @param event: Event object
        @return: list of EventModerationMessage
        """

        return cls.objects.filter(event=event).select_related('author')


class EventModerationMessage(Message):

    class Meta:
        verbose_name = u'wiadomość moderacji wydarzenia'
        verbose_name_plural = u'wiadomości moderacji wydarzenia'

class EventMessage(Message):

    class Meta:
        verbose_name = u'wiadomość wydarzenia'
        verbose_name_plural = u'wiadomości wydarzenia'