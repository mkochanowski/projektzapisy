# -*- coding: utf-8 -*-

__author__ = 'maciek'

FEREOL_PATH = '../'

import sys
import os
from django.core.management import setup_environ
from datetime import time



if __name__ == '__main__':
    sys.path.append(FEREOL_PATH)
    sys.path.append(FEREOL_PATH + 'fereol/')
    from fereol import settings
    setup_environ(settings)



from apps.users.models import Student
from django.core.exceptions import ObjectDoesNotExist
from apps.enrollment.courses.models.course import Course
from apps.offer.vote.models import SingleVote


#students = Student.objects.filter(status=0, ects=0)
#
#for s in students:
#    s.records_opening_bonus_minutes = 1440
#    s.save()


f = open("pierwszaki.txt", "r")


lista = []

lista.append(Course.objects.get(name=u"Algebra"))
lista.append(Course.objects.get(name=u"Programowanie (L)"))
lista.append(Course.objects.get(name=u"Programowanie (M)"))
lista.append(Course.objects.get(name=u"Programowanie obiektowe"))
lista.append(Course.objects.get(name=u"Kurs języka C++"))
lista.append(Course.objects.get(name=u"Kurs języka Pascal"))
lista.append(Course.objects.get(name=u"Kurs: tworzenie aplikacji interaktywnych w Pythonie"))



for l in f:

    pola = l.split()

    try:
        s = Student.objects.get(matricula=pola[-2])
    except ObjectDoesNotExist:
        print "Nie znaleziona studenta " + pola[-2]
        continue

    if s.ects > 0:
        print "Student " + pola[-2] + " powtarza"
        continue

    #s.records_opening_bonus_minutes += int(pola[-1])

    for p in lista:
        v = SingleVote()
        v.student = s
        v.course = p
        v.entity = p.entity
        v.value = 3
        v.correction = 3
        v.save()

    #s.save()