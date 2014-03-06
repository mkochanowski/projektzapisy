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
        s25   = Classroom.objects.get(number='25')
        s141 = Classroom.objects.get(number='141')
        s139 = Classroom.objects.get(number='139')
        s140 = Classroom.objects.get(number='140')
        s103 = Classroom.objects.get(number='103')
        s104 = Classroom.objects.get(number='104')
        s105 = Classroom.objects.get(number='105')
        s108 = Classroom.objects.get(number='108')
        s110 = Classroom.objects.get(number='110')
        s119 = Classroom.objects.get(number='119')
        s237 = Classroom.objects.get(number='237')
        s310 = Classroom.objects.get(number='310')

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

        def create_event(title, visible=True):
            ev = Event()
            ev.title = title
            ev.type   = '4'
            ev.visible = visible
            ev.status  = '1'
            ev.author_id = 1
            ev.save()

            return ev

        def create_term(event, day, start, end, room, minutes_start = 0, minutes_end=0):
            newTerm = Term()
            newTerm.event = event
            newTerm.day = day
            newTerm.start = timedelta(hours=start, minutes=minutes_start)
            newTerm.end = timedelta(hours=end, minutes=minutes_end)
            newTerm.room = room
            newTerm.save()


        for d in days[4]: #piatek
            ev = create_event('Dziennikarze')

            create_term(ev, d, 15, 22, s4)
            create_term(ev, d, 15, 22, s5)
            create_term(ev, d, 15, 22, s104)
            create_term(ev, d, 15, 22, s103)
            create_term(ev, d, 15, 22, s139)
            create_term(ev, d, 15, 22, s140)
            create_term(ev, d, 15, 22, s141)


            sem = create_event('Seminarium ZJP')
            create_term(sem, d, 14, 16, s105)

            kol = create_event('Inst. Matematyczny')
            create_term(sem, d, 12, 14, s25)

            kol = create_event('Kolokwia')
            create_term(sem, d, 14, 16, s25)

        for d in days[5]: #sobota
            ev = create_event('Dziennikarze')

            create_term(ev, d, 8, 22, s4)
            create_term(ev, d, 8, 22, s5)
            create_term(ev, d, 8, 22, s104)
            create_term(ev, d, 8, 22, s103)
            create_term(ev, d, 8, 22, s139)
            create_term(ev, d, 8, 22, s140)
            create_term(ev, d, 8, 22, s141)


        for d in days[6]: #niedziela
            ev = create_event('Dziennikarze')

            create_term(ev, d, 8, 22, s4)
            create_term(ev, d, 8, 22, s5)
            create_term(ev, d, 8, 22, s104)
            create_term(ev, d, 8, 22, s103)
            create_term(ev, d, 8, 22, s139)
            create_term(ev, d, 8, 22, s140)
            create_term(ev, d, 8, 22, s141)

        for d in days[0]: #poniedzialke
            ev = create_event('Dziennikarze')
            create_term(ev, d, 10, 14, s4)
            create_term(ev, d, 15, 20, s110)

            ang = create_event('Jezyk Angielski')
            create_term(ang, d, 8, 12, s5)


        for d in days[1]: #wtorek
            radaw = create_event('Rada Wydzialu')
            create_term(radaw, d, 12, 14, s119)

            net = create_event('grupa .NET')
            create_term(net, d, 18, 20, s119)


            sem = create_event('Seminarium ZMN')
            create_term(sem, d, 14, 16, s104)
            create_term(sem, d, 14, 16, s237)


            sem = create_event('Seminarium PIO')
            create_term(sem, d, 16, 18, s103)


            sem = create_event('kolokwium AiSD')
            create_term(sem, d, 14, 15, s25)
            create_term(sem, d, 14, 15, s119)


        for d in days[2]: #sroda
            ev = create_event('seminarium PGK')
            create_term(ev, d, 12, 14, s105)


        for d in days[3]: #czwartek
            ev = create_event('Dziennikarze')
            create_term(ev, d, 12, 14, s5)


            sem = create_event('Seminarium Insytutowe')
            create_term(sem, d, 14, 16, s119)

            sem = create_event('Seminarium ZZOiA')
            create_term(sem, d, 12, 14, s103)

            sem = create_event('Seminarium ZOK')
            create_term(sem, d, 12, 14, s310)

            ksi = create_event('KSI')
            create_term(ksi, d, 20, 22, s119)
