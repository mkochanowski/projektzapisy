# -*- coding: utf-8 -*-


__author__ = 'maciek'

FEREOL_PATH = '../'

import sys
import os
from django.core.management import setup_environ
from datetime import time


class ImportS():
	def __init__(self):
		from apps.users.models import Student, UserProfile, Program
		from django.contrib.auth.models import User
		from apps.enrollment.courses.models import Semester
                count = 0
		f = open('Iyear', 'r')
		for line in f:
		   a = line.split()
		   matricula = a[0]
		   name = a[1]
		   last = a[2]
		   password = a[3].split(':')[1]
		   print matricula
		   try:
			   user = User.objects.create_user(matricula, password=password)
			   user.first_name = name
			   user.last_name  = last
			   user.save()

			   UserProfile.objects.create(user=user, is_student=True)

			   student = Student()
			   student.user = user
			   student.matricula = matricula
			   student.program_id = 4
			   student.semestr = 1
			   student.save()
                           count += 1
			   print matricula + ' imported'

		   except:
                        print "zle"

		f.close()
                print count


if __name__ == '__main__':
    sys.path.append(FEREOL_PATH)
    sys.path.append(FEREOL_PATH + 'fereol/')
    from fereol import settings
    setup_environ(settings)
    ImportS()

