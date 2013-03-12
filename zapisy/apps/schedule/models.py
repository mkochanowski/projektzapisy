# -*- coding: utf-8 -*-
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.query import EmptyQuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode
from timedelta import TimedeltaField
import json
from mailer.utils import render_and_send_email
import settings

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
    reservation = models.ForeignKey('schedule.SpecialReservation',  null=True, blank=True)

    interested  = models.ManyToManyField('auth.User', related_name='interested_events')

    author      = models.ForeignKey('auth.User', verbose_name=u'Twórca')
    created     = models.DateTimeField(auto_now_add=True)
    edited      = models.DateTimeField(auto_now=True)


    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        if self.group:
            return reverse('records-group', args=[str(self.group_id)])
        return reverse('events:show', args=[str(self.pk)])

    class Meta:
        verbose_name = u'wydarzenie'
        verbose_name_plural = u'wydarzenia'
        ordering = ('-created',)
        permissions = (
            ("manage_events", u"Może zarządzać wydarzeniami"),
        )


    def save(self, *args, **kwargs):
        """
        Overload save method.
        If author is employee and try reserve room for exam - accept it
        If author has perms to manage events - accept it
        """
        is_new = False

        if not self.pk:
            is_new = True
            if (self.author.employee and self.type in ['0','1']) or \
                self.author.has_perm('schedule.manage_events'):
                self.status = '1'

            if self.type in ['0','1']:
                self.visible = True


        super(self.__class__, self).save()

        if is_new and self.type in ['0','1'] and self.course:
            render_and_send_email(u'Ustalono termin egzaminu',
                                   u'schedule/emails/new_exam.txt',
                                   u'schedule/emails/new_exam.html',
                                   {'event': self},
                                   self.get_followers()
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
    def get_all_without_courses(cls):
        """

        Return all events with all needed select_related and prefetch_related

        @return: Event QuerySet
        """
        return cls.get_all().exclude(type='3')

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
        return cls.objects.filter(type='0', status='1').order_by('-created').select_related('course', 'course__entity')

    @classmethod
    def get_events(cls):
        """
        """

        return cls.objects.filter(status='1', type='0').order_by('-created')

    def get_followers(self):
        if self.type in ['0', '1']:
            return self.course.get_all_enrolled_emails()

        return self.interested.values_list('email', flat=True)


class Term(models.Model):
    """
    Term representation
    """
    event = models.ForeignKey(Event, verbose_name=u'Wydarzenie')

    day = models.DateField(verbose_name=u'Dzień')

    start = TimedeltaField(verbose_name=u'Początek')
    end   = TimedeltaField(verbose_name=u'Koniec')

    room  = models.ForeignKey('courses.Classroom', null=True, blank=True, verbose_name=u'Sala', related_name='event_terms')
    place = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'Miejsce')

    def validate_unique(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        from django.db.models import Q

        if self.room:
            terms = self.__class__.objects.filter(Q(room=self.room), Q(day=self.day), Q(event__status='1'),
            Q(start__lt=self.end))\
                                .select_related('event')

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
        get_latest_by = 'end'
        ordering = ['day', 'start', 'end']
        verbose_name = u'termin'
        verbose_name_plural = u'terminy'

    def get_conflicted(self):

        if not self.room:
            return EmptyQuerySet()

#        X < B AND A < Y

        terms = Term.objects.filter(Q(room=self.room), Q(day=self.day),
                                    Q(start__lt=self.end), Q(end__gt=self.start))\
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
        return cls.objects.filter(event__type__in=['0', '1']).order_by('day', 'event__course__entity__name', 'room')\
        .select_related('event', 'room', 'event__course', 'event__course__entity', 'event__course__semester')


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


    def save(self, *args, **kwargs):
        super(EventModerationMessage, self).save(*args, **kwargs)
        if self.author == self.event.author:
            to = settings.EVENT_MODERATOR_EMAIL
        else:
            to = self.author.email

#        render_and_send_email(u'Nowa wiadomość moderatorska w wydarzeniu',
#                               u'schedule/emails/new_moderation_message.txt',
#                               u'schedule/emails/new_moderation_message.html',
#                               {'event': self.event},
#                               [to]
#        )

class EventMessage(Message):

    class Meta:
        verbose_name = u'wiadomość wydarzenia'
        verbose_name_plural = u'wiadomości wydarzenia'

    def save(self, *args, **kwargs):
        super(EventMessage, self).save(*args, **kwargs)

#
#        render_and_send_email(u'Nowa wiadomość w wydarzeniu',
#                               u'schedule/emails/new_message.txt',
#                               u'schedule/emails/new_message.html',
#                               {'event': self.event},
#                               self.event.get_followers()
#        )


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
        verbose_name = u'rezerwacja stała'
        verbose_name_plural = u'rezerwacje stałe'

    def __unicode__(self):
        return smart_unicode(self.semester) + ': ' + smart_unicode(self.title) + ' - ' + smart_unicode(self.get_dayOfWeek_display()) +\
                  ' ' + smart_unicode(self.start_time) + ' - ' + smart_unicode(self.end_time)

    def save(self, *args, **kwargs):
        from apps.enrollment.courses.models import Freeday, ChangedDay, Classroom

        super(SpecialReservation, self).save(*args, **kwargs)

        Event.objects.filter(reservation=self).delete()

        semester = self.semester

        freedays = Freeday.objects.filter(Q(day__gte=semester.lectures_beginning),
                                          Q(day__lte=semester.lectures_ending))\
                          .values_list('day', flat=True)

        changed = ChangedDay.objects.filter(Q(day__gte=semester.lectures_beginning), Q(day__lte=semester.lectures_ending)).values_list('day', 'weekday')
        days = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        day = semester.lectures_beginning

        while day <= semester.lectures_ending:

            if day in freedays:
                day = day + datetime.timedelta(days=1)
                continue

            weekday = day.weekday()

            for d in changed:
                if d[0] == day:
                    weekday = int(d[1]) - 1
                    break

            days[weekday].append(day)
            day = day + datetime.timedelta(days=1)

        ev = Event()
        ev.title  = self.title
        ev.reservation = self
        ev.type   = '4'
        ev.visible = True
        ev.status  = '1'
        ev.author_id = 1
        ev.save()

        for day in days[int(self.dayOfWeek) - 1]:
            newTerm = Term()
            newTerm.event = ev
            newTerm.day = day
            newTerm.start = datetime.timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
            newTerm.end   = datetime.timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)
            newTerm.room = self.classroom
            newTerm.save()
