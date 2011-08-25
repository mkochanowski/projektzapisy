# -*- coding: utf-8 -*-

#### TO CHANGE #####
SCHEDULE_FILE = '/home/gosia/Desktop/plan'
LIMITS = {'1' : 300, '9' : 300, '2' : 20, '3' : 15 , '5' : 18 , '6' : 15 }

O1 = ['analizamatematyczna','algebra','logikadlainformatyków','elementyrachunkuprawdopodobieństwa','metodyprobabilistyczneistatystyka']
O2 = ['matematykadyskretna','programowanie','analizanumeryczna','algorytmyistrukturydanych']
O3 = ['językiformalneizłożonośćobliczeniowa']
Oinz = ['fizykadlainformatyków','podstawyelektroniki,elektrotechnikiimiernictwa']
I1 = ['wstępdoinformatyki','architekturasystemówkomputerowych','bazydanych','systemyoperacyjne','siecikomputerowe','inżynieriaoprogramowania']
Iinz = ['systemywbudowane','podstawygrafikikomputerowej','sztucznainteligencja','komunikacjaczłowiek-komputer']
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
from apps.enrollment.courses.models import Course, Semester, CourseEntity, Type, Group, Term, Classroom, PointsOfCourseEntities, PointsOfCourses, PointTypes
from apps.users.models import Student, Employee, Program

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

def upper_pl(s):
    return s.upper().replace('ą','Ą').replace('ć','Ć').replace('ę','Ę').replace('ł','Ł').replace('ń','Ń').replace('ó','Ó').replace('ś','Ś').replace('ż','Ż').replace('ź','Ź')


def guess_type(name,COURSE_TYPE):
    name = lower_pl(name.replace(' ','').replace('(L)','').replace('(M)','').replace('(B)','()'))
    if name in O1:
        return COURSE_TYPE['O1'],'O1'
    elif name in O2:
        return COURSE_TYPE['O2'],'O2'
    elif name in O3:
        return COURSE_TYPE['O3'],'O3'
    elif name in Oinz:
        return COURSE_TYPE['Oinż'],'Oinż'
    elif name in I1:
        return COURSE_TYPE['I1'],'I1'
    elif name in Iinz:
        return COURSE_TYPE['Iinż'],'Iinż'
    elif 'kurs' in name:
        return COURSE_TYPE['K'],'K'
    elif 'seminarium' in name:
        return COURSE_TYPE['S'],'S'
    elif 'projekt' in name:
        return COURSE_TYPE['P'],'P'
    return COURSE_TYPE['I2'],'I2'

def find_teacher(t):
    teacher_full_name = map(lambda x: len(x)>0 and x[0]+lower_pl(x[1:]) or x,t.split(' '))
    if len(teacher_full_name)==1:
        teacher_name = ''
        teacher_surname = teacher_full_name[0]
    if len(teacher_full_name)==2:
        teacher_name = teacher_full_name[0]
        teacher_surname = teacher_full_name[1] 
    if len(teacher_full_name)==3:
        teacher_name = teacher_full_name[0]+' '+teacher_full_name[1]
        teacher_surname = teacher_full_name[2]
    teachers = Employee.objects.filter(user__first_name=teacher_name, user__last_name=teacher_surname)

    if len(teachers)==0:
        username = teacher_name+teacher_surname
        teacher_surname = teacher_surname.replace('Denivelle','de Nivelle')
        user = User.objects.get_or_create(first_name=teacher_name, last_name=teacher_surname, username=username)[0]
        teacher = Employee.objects.create(user=user, consultations="")
    elif len(teachers)>1:
        print 'Error: more then one teacher of name: %s, and surname: %s.' % (teacher_name,teacher_surname)
    else:
        teacher = teachers[0]
    return teacher

def guess_points(name,t):
    name = lower_pl(name.replace(' ','').replace('(L)','').replace('(M)','').replace('(B)','()'))
    if t=='O1':
        if name=='analizamatematyczna':
            return 10,10
        elif name in ['algebra','logikadlainformatyków']:
            return 7,7
        elif name=='elementyrachunkuprawdopodobieństwa':
            return 3,3
        elif name=='metodyprobabilistyczneistatystyka':
            return 6,6
    elif t=='O2':
        if name=='matematykadyskretna':
            return 6,9
        elif name=='programowanie':
            return 9,12
        elif name=='analizanumeryczna':
            return 8,12
        elif name=='algorytmyistrukturydanych':
            return 9,13
    elif t=='O3':
        return 9,9
    elif t=='Oinż':
        if name=='fizykadlainformatyków':
            return 6,6
        elif name=='podstawyelektroniki,elektrotechnikiimiernictwa':
            return 4,4
    elif t=='I1':
        return 6,6
    elif t=='Iinż':
        return 6,6
    elif t=='K':
        return 5,5
    elif t=='S':
        return 3,3
    elif t=='P':
        return 4,4
    return 6,6

def get_classroom(rooms):
    try:
        room = rooms[0] #FIXIT
        if room.replace(' ','')=='':
            classroom = Classroom.objects.get_or_create(number='0')[0]
        else:
            classroom = Classroom.objects.get_or_create(number=room)[0]
    except IndexError:
        classroom = Classroom.objects.get_or_create(number='0')[0]

    return classroom

def get_points_values():
    ects = PointTypes.objects.get_or_create(name='ECTS')[0]
    program_lic = Program.objects.get_or_create(name='', type_of_points=ects)[0]
    program_mgr = Program.objects.get_or_create(name='', type_of_points=ects)[0]
    return ects, program_lic, program_mgr

def import_schedule(file, semester):
    types = [('Informatyczny 1','I1'),
            ('Informatyczny 2','I2'),
            ('Informatyczny inż.','Iinż'),
            ('Obowiązkowy 1','O1'),
            ('Obowiązkowy 2','O2'),
            ('Obowiązkowy 3','O3'),
            ('Obowiązkowy inż.','Oinż'),
            ('Kurs','K'), 
            ('Projekt','P'), 
            ('Seminarium','S'), 
            ('Nieinformatyczny','N'), 
            ('Wychowanie fizyczne','WF'), 
            ('Lektorat','L'), 
            ('Inne','?')]

    COURSE_TYPE = {}

    ects, program_lic, program_mgr = get_points_values()

    for t in types:
        td = Type.objects.get_or_create(name=t[0], meta_type=False, defaults = {'short_name':t[1], 'group':None})[0]
        COURSE_TYPE[t[1]] = td

    course = None
    while True:
        line = file.readline()
        if not line:
            return
        if line.startswith('  '):
            if line.replace(' ','')=='\n':
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
                
                t = 15*(int(g.group('end_time'))-int(g.group('start_time')))
                print t
                if group_type=='1':
                    lectures += t
                elif group_type=='9':
                    repetitions += t
                elif group_type=='2':
                    exercises = exercises and exercises or t
                elif group_type=='3':
                    laboratories = laboratories and laboratories or t
                elif group_type=='5':
                    exercises_laboratories = exercises_laboratories and exercises_laboratories or t
                    
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
            if line==' \n':
                continue
            
            if course:
                course.lectures, course.exercises, course.laboratories, course.repetitions, course.exercises_laboratories = lectures, exercises, laboratories, repetitions, exercises_laboratories
                course.save()
            name = line[1:-1]
            if name.startswith('SEMINARIUM: '):
                extra = 'Seminarium: '
                name = name.replace('SEMINARIUM: ','')
            elif name.startswith('PROJEKT: '):
                extra = 'Projekt: '
                name = name.replace('PROJEKT: ','')
            else:
                extra = ''
            name = len(name)>0 and name[0]+lower_pl(name[1:]) or name
            name = name.replace('(l)','(L)').replace('(m)','(M)').replace('(b)','(B)')
            name = extra+name
            name = name.replace('python','Python').replace('java','Java').replace('linux','Linux').replace('ansi c','ANSI C').replace('Ccna','CCNA').replace('www','WWW').replace('c++','C++').replace('asp.net','ASP.NET').replace('silverlight','Silverlight')
            shortName = name[:29]
            entity = CourseEntity.objects.get_or_create(name=name,shortName=shortName)[0]
            lectures, exercises, laboratories, repetitions, exercises_laboratories = 0,0,0,0,0

            slug = str(semester.year) + semester.type + '_' + slugify(name)
            print slug
            type,short_type = guess_type(name,COURSE_TYPE)
            try:
                course = Course.objects.create(name=name,
                                                 entity=entity,
                                                 semester=semester,
                                                 slug = slug,
                                                 type=type
                                                 )
                
                points = PointsOfCourseEntities.objects.filter(entity=entity)
                '''
                for p in points:
                    type_of_point = p.type_of_point
                    value = p.value
                    poc = PointsOfCourses.objects.create(course=course, type_of_point=type_of_point, value=value)
                '''
                value_lic, value_mgr = guess_points(name,short_type)
                
                if not points:
                     PointsOfCourseEntities.objects.create(entity=entity,type_of_point=ects,value=value_mgr)
                    
                PointsOfCourses.objects.create(course=course,type_of_point=ects,program=program_lic,value=value_lic)
                PointsOfCourses.objects.create(course=course,type_of_point=ects,program=program_mgr,value=value_mgr)

            except Exception, e:
                print 'Error during creating course:%s. \nError: %s ' % (name, e)

        else:
            continue

def get_semester():
    today = datetime.today()
    type = today.month in [12,1,2,3,4,5] and 'l' or 'z'
    year = today.year
    next_year = (year+1)%100
    year = str(year)+'/'+str(next_year)
    semester_beginning = today
    semester_ending = today 
    semester = Semester.objects.get_or_create(type=type,
                                              year=year,
                                              defaults = {
                                                  'visible' : False,
                                                  'semester_beginning' : semester_beginning,
                                                  'semester_ending' : semester_ending})[0]
    return semester

@transaction.commit_on_success
def scheduleimport(data):
    semester = get_semester()
    file = data
    #file = open(SCHEDULE_FILE)
    import_schedule(file, semester)

#scheduleimport('')

