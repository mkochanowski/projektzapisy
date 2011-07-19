# -*- coding: utf-8 -*-

"""
Eksportuje przedmioty zwracane przez visible manager.

Zwracany format:

<format> := <podstawy przedmiotów><przedmioty>

<podstawy przedmiotów> := ======\n\n<podstawa przedmiotu>*\n\n======\n\n
<podstawa przedmiotu> := <kod przedmiotu w fereolu>\t<nazwa przedmiotu w fereolu>\t<rodzaj przedmiotu>\n

<przedmioty> := <przedmiot>*
<przedmiot> := <nazwa>\n<kod podstawy tego przedmiotu w fereolu>\n<kod tego przedmiotu w fereolu>\n<opis>\n<prowadzacy>\n<angielski>\n<grupy>\n======\n\n

<grupy> := (<grupa>\n)*
<grupa> := GRUPA\t<kod grupy w fereolu>\t<kod przedmiotu tej grupy>\t<prowadzacy1>\t<limit>\t<rodzaj zajec>\t<limit zamawianych>\t<terminy>

<prowadzacy> := (<prowadzacy1>;)*<prowadzacy1>
<prowadzacy1> := <imie z nazwiskiem>

<rodzaj przedmiotu> := O|I|K|P|S|N|WF|L|?
<rodzaj zajec> := w|c|p|C|r|s|l
<angielski> := 0|1

<terminy> := (<termin>;)*<termin>
<termin> := <dzien tygodnia>-<poczatek>-<koniec>-<sala>
<dzien> := <czas>
<koniec> := <czas>
<czas> := hh:mm:ss
<dzien tygodnia> := 1|2|3|4|5|6|7 

"""

FEREOL_PATH = '../..'

import sys
import os
from django.core.management import setup_environ
from datetime import time

if __name__ == '__main__':
    sys.path.append(FEREOL_PATH)
    sys.path.append(FEREOL_PATH + '/fereol')
    from fereol import settings
    setup_environ(settings)

from apps.enrollment.records.models import Record, STATUS_ENROLLED
from apps.enrollment.courses.models import Course, Semester, CourseEntity, Type, Group, Term, Classroom, PointsOfCourseEntities, PointsOfCourses
from apps.users.models import Student, Employee

from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db import transaction

from datetime import datetime
import re

"""
Uwagi:
* wf jest lektoratem
* repetytorium wykładem
* projekt pracownią
"""
f = open('asdf','a')

GROUP_TYPE_CHOICES = {'1': 'w', '2': 'c', '3': 'p',
        '4': 'C', '5': 'r',
        '6': 's', '7': 'l', '8': 'l',
        '9': 'w', '10': 'p'}

def export():
    courses = Course.visible.select_related().all()
    entities = set([c.entity for c in courses])
    
    f.write('======\n\n')
    
    for entity in entities:
        kod_przed = entity.id
        nazwa = entity.name
        try:
            typ = entity.type.name
        except:
            typ = "XXX"
        f.write('%s\t%s\t%s\n' % (kod_przed,nazwa,typ))
    
    f.write('\n\n======\n\n')
    
    for course in courses:
        kod_przed_sem = course.id
        kod_przed = course.entity.id
        nazwa = course.name
        opis = course.description.replace('\n','')
        kod_uz = ';'.join([t.user.get_full_name() for t in course.teachers.all()])
        if kod_uz=='':
            kod_uz='XXX'
        angielski = 1
        f.write('%s\n%s\n%s\n%s\n%s\n%s\n' % (nazwa,kod_przed_sem,kod_przed,opis,kod_uz,angielski))
        
        groups = course.groups.all()
        for group in groups:
            kod_grupy = group.id 
            kod_przed_sem
            kod_uz = group.teacher and group.teacher.user.get_full_name() or "XXX"
            max_osoby = group.limit
            rodzaj_zajec = GROUP_TYPE_CHOICES[group.type]
            zamawiane_bonus = group.limit_zamawiane
            terminy = ';'.join(['-'.join([t.dayOfWeek,str(t.start_time),str(t.end_time),t.classroom.number]) for t in group.term.all()])
            f.write('GRUPA\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (kod_grupy,kod_przed_sem,kod_uz,max_osoby,rodzaj_zajec,zamawiane_bonus,terminy))
    
        f.write('\n======\n\n')
    

export()
