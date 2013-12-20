# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.db.models import Q
from django.utils.encoding import smart_unicode


class SpecialReservation(models.Model):
    #from apps.enrollment.courses.models import Semester, DAYS_OF_WEEK, Classroom

    #semester = models.ForeignKey(Semester)
    title = models.CharField(max_length=255)
    #classroom = models.ForeignKey(Classroom)
    #dayOfWeek = models.CharField(max_length=1,
    #                             choices=DAYS_OF_WEEK,
    #                             verbose_name='dzień tygodnia')
    start_time = models.TimeField(verbose_name='rozpoczęcie')
    end_time = models.TimeField(verbose_name='zakończenie')

    class Meta:
        app_label = 'schedule'
        verbose_name = u'rezerwacja stała'
        verbose_name_plural = u'rezerwacje stałe'

    def __unicode__(self):
        return '%s: %s - %s %s - %s'.format(smart_unicode(self.semester), smart_unicode(self.title),
                                            smart_unicode(self.get_dayOfWeek_display()), smart_unicode(self.start_time),
                                            smart_unicode(self.end_time))

    def save(self, *args, **kwargs):
        from apps.enrollment.courses.models import Freeday, ChangedDay
        from apps.schedule.models import Event, Term

        super(SpecialReservation, self).save(*args, **kwargs)

        Event.objects.filter(reservation=self).delete()

        semester = self.semester

        freedays = Freeday.objects.filter(Q(day__gte=semester.lectures_beginning),
                                          Q(day__lte=semester.lectures_ending))\
                          .values_list('day', flat=True)

        changed = ChangedDay.objects.filter(Q(day__gte=semester.lectures_beginning),
                                            Q(day__lte=semester.lectures_ending)).values_list('day', 'weekday')
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
        ev.title = self.title
        ev.reservation = self
        ev.type = '4'
        ev.visible = True
        ev.status = '1'
        ev.author_id = 1
        ev.save()

        for day in days[int(self.dayOfWeek) - 1]:
            newTerm = Term()
            newTerm.event = ev
            newTerm.day = day
            newTerm.start = datetime.timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
            newTerm.end = datetime.timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)
            newTerm.room = self.classroom
            newTerm.save()
