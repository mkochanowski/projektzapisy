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

f = open("plik.txt", "r")

vote_list = []

for line in f:
    l = line.split('|')
    vote_list.append((l[0].strip(), int(l[1].strip()), l[2].strip()))

from django.core.exceptions import ObjectDoesNotExist
from apps.enrollment.courses.models.course import CourseEntity, Course
from apps.enrollment.courses.models.semester import Semester
from apps.offer.vote.models.single_vote import SingleVote
from apps.offer.vote.models.system_state import SystemState, DEFAULT_MAX_POINTS
from apps.users.models import Student
semester = Semester.get_current_semester()

try:
    state = SystemState.objects.get(semester_summer=semester)
except ObjectDoesNotExist:
    state = SystemState()
    state.year = 1999
    state.semester_winter = semester
    state.semester_summer = semester
    state.save()

byly = {}
przedmioty = {}
users = {}

for nazwa, glos, osoba in vote_list:


    if not nazwa in przedmioty:

        try:
            entity = CourseEntity.objects.get(name__iexact=nazwa)
            course = Course.objects.get(entity=entity, semester=semester)

            przedmioty[nazwa] = (entity, course)
        except ObjectDoesNotExist:
            if not nazwa in byly:
                print "Nie znaleziono: " + nazwa
                byly[nazwa] = True
            continue
    else:
        entity, course = przedmioty[nazwa]

    if not osoba in users:
        try:
            student = Student.objects.get(matricula=osoba)
            users[osoba] = student
        except ObjectDoesNotExist:
            print "Nie znaleziono: " + osoba
            continue
    else:
        student = users[osoba]

    try:
        vote = SingleVote.objects.get(student=student, state=state, course=course)
        continue
    except ObjectDoesNotExist:
        vote = SingleVote()

    vote.student    = student
    vote.entity     = entity
    vote.course     = course
    vote.state      = state
    vote.value      = glos
    vote.correction = glos
    vote.save()