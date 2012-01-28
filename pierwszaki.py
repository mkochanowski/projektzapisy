# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist


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


students = Student.objects.filter(status=0, ects=0)

for s in students:
    s.records_opening_bonus_minutes = 1440
    s.save()


f = open("pierwszaki.txt", "r")

for l in f:

    pola = l.split()

    print "Przetwarzanie: " + pola[-2] + " " + pola[-1]
    try:
        s = Student.objects.get(matricula=pola[-2])
    except ObjectDoesNotExist:
        print "Nie znaleziona studenta " + pola[-2]
        continue

    if s.ects > 0:
        print "Student " + pola[-2] + " powtarza"
        continue

    s.records_opening_bonus_minutes += int(pola[-1])


    # s.save()