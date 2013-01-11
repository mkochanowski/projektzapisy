# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta
from django.core.management import BaseCommand
from django.db.models import Q
from apps.enrollment.courses.models import Semester, Freeday, ChangedDay, Classroom
from apps.enrollment.courses.models import Term as T
from apps.schedule.models import Term, Event


class Command(BaseCommand):

    def handle(self, *args, **options):
        semester = Semester.get_current_semester()

        freedays = Freeday.objects.filter(Q(day__gte=semester.lectures_beginning),
                                          Q(day__lte=semester.lectures_ending))\
                          .values_list('day', flat=True)
        changed = ChangedDay.objects.filter(Q(day__gte=semester.lectures_beginning), Q(day__lte=semester.lectures_ending)).values_list('day', 'weekday')
        days = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        day = semester.lectures_beginning


        s4   = Classroom.objects.get(number='4')
        s5   = Classroom.objects.get(number='5')
        s141 = Classroom.objects.get(number='141')
        s139 = Classroom.objects.get(number='139')
        s140 = Classroom.objects.get(number='140')

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

        for d in days[4]:
            ev = Event()
            ev.title ='Dziennikarze'
            ev.type   = '4'
            ev.visible = False
            ev.status  = '1'
            ev.author_id = 1
            ev.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=14, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s4
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=14, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s5
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=14, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s139
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=14, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s140
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=14, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s141
            newTerm.save()

        for d in days[5]:
            ev = Event()
            ev.title ='Dziennikarze'
            ev.type   = '4'
            ev.visible = False
            ev.status  = '1'
            ev.author_id = 1
            ev.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s4
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s5
            newTerm.save()


            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s139
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s140
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s141
            newTerm.save()


        for d in days[6]:
            ev = Event()
            ev.title ='Dziennikarze'
            ev.type   = '4'
            ev.visible = False
            ev.status  = '1'
            ev.author_id = 1
            ev.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s4
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s5
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s139
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s140
            newTerm.save()

            newTerm = Term()
            newTerm.event = ev
            newTerm.day = d
            newTerm.start = timedelta(hours=8, minutes=0)
            newTerm.end = timedelta(hours=22, minutes=0)
            newTerm.room = s141
            newTerm.save()


