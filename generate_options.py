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

from apps.enrollment.courses.models.semester import Semester
from apps.offer.vote.models.system_state import SystemState
from apps.enrollment.courses.models.student_options import StudentOptions
from apps.offer.vote.models.single_vote import SingleVote



semester = Semester.get_current_semester()
state    = SystemState.objects.get(semester_summer=semester)


for vote in SingleVote.objects.filter(state=state, course__semester=semester):
    option = StudentOptions()
    option.student = vote.student
    option.course  = vote.course
    option.records_opening_bonus_minutes = vote.correction * 1440
    option.save()

