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

from django.core.exceptions import ObjectDoesNotExist
from apps.users.models import Student, Program


for user in Student.objects.using('fereol2012').all():
    try:
        u = Student.objects.get(matricula=user.matricula)
    except ObjectDoesNotExist:
        print "User nieznaleziony: " + user.matricula
        continue

    if u.ects >= user.ects:
        print "Brak zmiany ECTS " + user.matricula

    u.ects = max(u.ects, user.ects)
    u.semestr = user.semester
    if user.status == 1:
        print "User o numerze " + user.matricula + " skreslony"

    u.status = user.status

    try:
        u.program = Program.objects.get(id= user.program_id)
    except ObjectDoesNotExist:
        print "Program nieznaleziony: " + user.program

    #u.save()

