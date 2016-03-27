# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404
from datetime import time


class Event(models.Model):
    """
    Model of Event
    """
    TYPE_EXAM = '0'
    TYPE_TEST = '1'
    TYPE_EVENT = '2'
    TYPE_CLASS = '3'
    TYPE_OTHER = '4'

    STATUS_PENDING = '0'
    STATUS_ACCEPTED = '1'
    STATUS_REJECTED = '2'

    STATUSES = [(STATUS_PENDING, u'Do rozpatrzenia'),
                (STATUS_ACCEPTED, u'Zaakceptowane'),
                (STATUS_REJECTED, u'Odrzucone')]

    TYPES = [(TYPE_EXAM, u'Egzamin'),
             (TYPE_TEST, u'Kolokwium'),
             (TYPE_EVENT, u'Wydarzenie'),
             (TYPE_CLASS, u'Zajęcia'),
             (TYPE_OTHER, u'Inne')]

    TYPES_FOR_STUDENT = [(TYPE_EVENT, u'Wydarzenie')]

    TYPES_FOR_TEACHER = [(TYPE_EXAM, u'Egzamin'),
                         (TYPE_TEST, u'Kolokwium'),
                         (TYPE_EVENT, u'Wydarzenie')]

    from apps.enrollment.courses.models import Course, Group
    from django.contrib.auth.models import User

    title = models.CharField(max_length=255, verbose_name=u'Tytuł', null=True, blank=True)
    description = models.TextField(verbose_name=u'Opis')
    type = models.CharField(choices=TYPES, max_length=1, verbose_name=u'Typ')
    visible = models.BooleanField(verbose_name=u'Wydarzenie jest publiczne')

    status = models.CharField(choices=STATUSES, max_length=1, verbose_name=u'Stan', default='0')

    course = models.ForeignKey(Course, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)
    reservation = models.ForeignKey('schedule.SpecialReservation', null=True, blank=True)

    interested = models.ManyToManyField(User, related_name='interested_events')

    author = models.ForeignKey(User, verbose_name=u'Twórca')
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse

        if self.group:
            return reverse('records-group', args=[str(self.group_id)])
        return reverse('events:show', args=[str(self.pk)])

    class Meta:
        app_label = 'schedule'
        verbose_name = u'wydarzenie'
        verbose_name_plural = u'wydarzenia'
        ordering = ('-created',)
        permissions = (
            ("manage_events", u"Może zarządzać wydarzeniami"),
        )

    # This code should be in clean() method
    def save(self, *args, **kwargs):
        """
        Overload save method.
        If author is employee and try reserve room for exam - accept it
        If author has perms to manage events - accept it
        """
        is_new = False

        if not self.pk:
            is_new = True
            if (self.author.employee and self.type in ['0', '1']) or \
                    self.author.has_perm('schedule.manage_events'):
                self.status = '1'

            if self.type in ['0', '1']:
                self.visible = True

        super(self.__class__, self).save()

    #        if is_new and self.type in ['0', '1'] and self.course:
    #            render_and_send_email(u'Ustalono termin egzaminu',
    #                                  u'schedule/emails/new_exam.txt',
    #                                  u'schedule/emails/new_exam.html',
    #                                  {'event': self},
    #                                  self.get_followers()
    #            )

    def _user_can_see_or_404(self, user):
        """

        Private method. Return True if user can see event, otherwise False.

        @param user: auth.User
        @return: Boolean
        """
        if not self.author == user and not user.has_perm('schedule.manage_events'):
            if not self.visible or self.type not in ['0', '1', '2'] or self.status != '1':
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
            event = cls.objects.select_related('group', 'course', 'course__entity', 'author') \
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
            event = cls.objects.select_related('group', 'course', 'course__entity', 'author') \
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
            event = cls.objects.select_related('group', 'course', 'course__entity', 'author') \
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
        return cls.objects.all().select_related('group', 'course', 'course__entity', 'author') \
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
        return cls.objects.filter(author=user).select_related('course', 'course__entity', 'author').prefetch_related(
            'term_set')

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

    @classmethod
    def get_events_for_dates(cls, dates, classroom, start_time=None, end_time=None):
        """
        Gets events with therms in specified classroom on specified days

        :param end_time: datetime.time
        :param start_time: datetime.time
        :param classroom: enrollment.courses.models.Classroom
        :param dates: datetime.date list
        """
        if start_time is None:
            start_time = time(8)
        if end_time is None:
            end_time = time(21)

        from .term import Term
        terms = Term.objects.filter(day__in=dates,
                                    start__lt=end_time,
                                    end__gt=start_time,
                                    room=classroom)

        return cls.objects.filter(term__in=terms)
