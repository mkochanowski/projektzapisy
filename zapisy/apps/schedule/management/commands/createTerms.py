# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta
from django.core.management import BaseCommand
from django.db.models import Q
from apps.enrollment.courses.models import Semester, Freeday, ChangedDay
from apps.enrollment.courses.models import Term as T
from apps.schedule.models import Term, Event


class Command(BaseCommand):

    def handle(self, *args, **options):
        semester = Semester.objects.get_next()

        freedays = Freeday.objects.filter(Q(day__gte=semester.lectures_beginning),
                                          Q(day__lte=semester.lectures_ending))\
                          .values_list('day', flat=True)
        changed = ChangedDay.objects.filter(Q(day__gte=semester.lectures_beginning), Q(day__lte=semester.lectures_ending)).values_list('day', 'weekday')
        terms    = T.objects.filter(group__course__semester=semester).select_related('group', 'group__course', 'group__course__courseentity')
        days = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        day = semester.lectures_beginning

        while day <= semester.lectures_ending:

            if day in freedays:
                day = day + timedelta(days=1)
                continue

            weekday = day.weekday()

            for d in changed:
                if d[0] == day:
                    weekday = int(d[1]) - 1
                    break

            days[weekday].append(day)

            day = day + timedelta(days=1)


        for t in terms:
            ev = Event()
            ev.group  = t.group
            ev.course = t.group.course
            ev.title  = ev.course.entity.get_short_name()
            ev.type   = '3'
            ev.visible = True
            ev.status  = '1'
            ev.author_id = 1
            ev.save()

            for room in t.classrooms.all():
                for day in days[int(t.dayOfWeek)-1]:
                    newTerm = Term()
                    newTerm.event = ev
                    newTerm.day = day
                    newTerm.start = timedelta(hours=t.start_time.hour, minutes=t.start_time.minute)
                    newTerm.end = timedelta(hours=t.end_time.hour, minutes=t.end_time.minute)
                    newTerm.room = room
                    newTerm.save()


