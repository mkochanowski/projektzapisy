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

            create_term(ev, d, 14, 22, s4)
            create_term(ev, d, 14, 22, s5)
            create_term(ev, d, 14, 22, s104)
            create_term(ev, d, 14, 22, s103)
            create_term(ev, d, 14, 22, s139)
            create_term(ev, d, 14, 22, s140)
            create_term(ev, d, 14, 22, s141)

            wf = create_event('WF', visible=False)

            create_term(wf, d, 19, 22, s119)

            sem = create_event('Seminarium ZJP')
            create_term(sem, d, 14, 16, s105)
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
            create_term(ev, d, 12, 14, s104)
            create_term(ev, d, 8, 12, s4)

            ang = create_event('Jezyk Angielski')
            create_term(ang, d, 8, 12, s5)


            grupa = create_event('MATEMATYKA: WSTEP DO INFORMATYKI I PROGRAMOWANIA (wyklad) RAFAL NOWAK')
            create_term(grupa, d, 14, 16, s25)
            
        for d in days[1]: #wtorek
            ev = create_event('Dziennikarze')
            create_term(ev, d, 8, 10, s4)
            create_term(ev, d, 12, 16, s4)

            rada = create_event('Rada Instytutu')
            create_term(rada, d, 12, 14, s310)


            radaw = create_event('Rada Wydzialu')
            create_term(radaw, d, 12, 16, s119)


            sem = create_event('Seminarium ZMN')
            create_term(sem, d, 14, 16, s104)
            create_term(sem, d, 14, 16, s237)


        for d in days[2]: #sroda
            ev = create_event('Dziennikarze')
            create_term(ev, d, 14, 18, s4)

            grupa = create_event('Grupa Wroclaw JUG')
            create_term(grupa, d, 18, 20, s119, minutes_start=30, minutes_end=30)

            grupa = create_event('MATEMATYKA: WSTEP DO INFORMATYKI I PROGRAMOWANIA (pracownia) WOJCIECH JEDYNAK')
            create_term(grupa, d, 16, 18, s108)

            grupa = create_event('MATEMATYKA: WSTEP DO INFORMATYKI I PROGRAMOWANIA (pracownia) RAFAL NOWAK')
            create_term(grupa, d, 16, 18, s110)


        for d in days[3]: #czwartek
            ev = create_event('Dziennikarze')
            create_term(ev, d, 12, 13, s4, minutes_end=15)

            ang = create_event('Jezyk Angielski')
            create_term(ang, d, 16, 20, s5)

            sem = create_event('Seminarium Insytutowe')
            create_term(sem, d, 14, 16, s119)

            sem = create_event('Seminarium ZZOiA')
            create_term(sem, d, 12, 14, s141)

            sem = create_event('Seminarium ZOK')
            create_term(sem, d, 12, 14, s310)

            sem = create_event('Seminarium PIO')
            create_term(sem, d, 14, 16, s104)