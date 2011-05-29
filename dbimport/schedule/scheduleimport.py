# -*- coding: utf-8 -*-

#### TO CHANGE #####
SCHEDULE_FILE = './PlanPrzedmiotów.txt'
LIMITS = {'1' : 200, '9' : 200, '2' : 20, '3' : 16 , '5' : 16 , '6' : 16 }
####  #####

FEREOL_PATH = '../../..'

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


regex = re.compile('\s+(?P<day>pn|wt|śr|czw|pi)\s+(?P<start_time>\d{1,2})-(?P<end_time>\d{1,2})\s+\((?P<type>wykład|repetytorium|ćwiczenia|pracownia|ćwicz\+pracownia|seminarium)\)\s+(?P<teacher>[^,]*),\s+(?P<rooms>.*)')

GROUP_TYPES = { 'wykład' : '1', 'repetytorium' : '9', 'ćwiczenia' : '2', 'pracownia' : '3' ,'ćwicz+pracownia' : '5' ,'seminarium' : '6' }

DAYS_OF_WEEK = { 'pn' : '1', 'wt' : '2', 'śr' : '3', 'czw' : '4', 'pi' : '5' }

def lower_pl(s):
    return s.lower().replace('Ą','ą').replace('Ć','ć').replace('Ę','ę').replace('Ł','ł').replace('Ń','ń').replace('Ó','ó').replace('Ś','ś').replace('Ż','ż').replace('Ź','ź')

def guess_type(name):
    return Type.objects.all()[0]

def find_teacher(t):
    teacher_full_name = map(lambda x: len(x)>0 and x[0]+lower_pl(x[1:]) or x,t.split(' '))
    if len(teacher_full_name)==1:
        teacher_name = ''
        teacher_surname = teacher_full_name[0]
    if len(teacher_full_name)==2:
        teacher_name = teacher_full_name[0]
        teacher_surname = teacher_full_name[1]
    if len(teacher_full_name)==3:
        teacher_name = teacher_full_name[0]+teacher_full_name[1]
        teacher_surname = teacher_full_name[2]
    teachers = Employee.objects.filter(user__first_name=teacher_name, user__last_name=teacher_surname)

    if len(teachers)==0:
        username = teacher_name+teacher_surname
        user = User.objects.create(first_name=teacher_name, last_name=teacher_surname, username=username)
        teacher = Employee.objects.create(user=user, consultations="a")
    elif len(teachers)>1:
        print 'Error: more then one teacher of name: %s, and surname: %s.' % (teacher_name,teacher_surname)
    else:
        teacher = teachers[0]
    return teacher


def get_classroom(rooms):
    try:
        room = rooms[0] #FIXIT
        classroom = Classroom.objects.get_or_create(number=room)[0]
    except IndexError:
        classroom = Classroom.objects.get_or_create(number='0')[0]

    return classroom
    

def import_schedule(file, semester):
    course = None
    while True:
        line = file.readline()
        if not line:
            return
        if line.startswith('  '):
            if line=='  \n':
                continue
            g = regex.match(line)
            try:
                dayOfWeek = DAYS_OF_WEEK[g.group('day')]
                start_time = time(hour=int(g.group('start_time')))
                end_time = time(hour=int(g.group('end_time')))
                rooms = g.group('rooms').replace(' ','').replace('sala','').replace('sale','').replace('\n','').split(',')
                classroom = get_classroom(rooms)

                group_type = GROUP_TYPES[g.group('type')]
                teacher = find_teacher(g.group('teacher'))
                limit = LIMITS[group_type]

                group = Group.objects.create(course=course,
                                             teacher=teacher,
                                             type=group_type,
                                             limit=limit)
                term = Term.objects.create(dayOfWeek=dayOfWeek,
                                           start_time=start_time,
                                           end_time=end_time,
                                           classroom=classroom,
                                           group=group)
                
            except AttributeError:
                print 'Error: line`'+line+'\' don\'t match regexp.'

        elif line.startswith(' '):
            name = lower_pl(line[1:-1])
            shortName = name[:29]
            entity = CourseEntity.objects.get_or_create(name=name,shortName=shortName)[0]

            slug = str(semester.year) + semester.type + '_' + slugify(name)
            try:
                course = Course.objects.create(name=name,
                                                 entity=entity,
                                                 semester=semester,
                                                 slug = slug,
                                                 )
                points = PointsOfCourseEntities.objects.filter(entity=entity)
                for p in points:
                    type_of_point = p.type_of_point
                    value = p.value
                    poc = PointsOfCourses.objects.create(course=course, type_of_point=type_of_point, value=value)


            except Exception, e:
                print 'Error during creating course:%s. \nError: %s ' % (name, e)

        else:
            continue

def get_semester():
    today = datetime.today()
    type = today.month in [12,1,2,3,4,5] and 'l' or 'z'
    year = today.year
    semester_beginning = today
    semester_ending = today 
    semester = Semester.objects.create(visible=False,
                                       type=type,
                                       year=year,
                                       semester_beginning=semester_beginning,
                                       semester_ending=semester_ending)
    return semester

def scheduleimport():
    semester = get_semester()
    file = open(SCHEDULE_FILE)
    import_schedule(file, semester)


scheduleimport()
