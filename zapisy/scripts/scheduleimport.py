# -*- coding: utf-8 -*-


from django.core.exceptions import ObjectDoesNotExist

SCHEDULE_FILE = 'plan.txt'
LIMITS = {'1' : 300, '9' : 300, '2' : 20, '3' : 15 , '5' : 18 , '6' : 15 }

FIRST_YEAR_FRIENDLY = ['logikadlainformatykpw','analizamatematyczna','algebra','kursjezykaansiczelementamic++','wstepdoinformatyki',
                       'wstepdoprogramowania','programowanie','programowanieobiektowe','kursjezykapascal',
                       'architekturysystempwkomputerowych', 'architekturasystempwkomputerowych']
O1 = ['analizamatematyczna','algebra','logikadlainformatykpw','elementyrachunkuprawdopodobienstwa','metodyprobabilistyczneistatystyka']
O2 = ['matematykadyskretna','programowanie','analizanumeryczna','algorytmyistrukturydanych']
O3 = ['jezykiformalneiz\xa3ożonosćobliczeniowa']
Oinz = ['fizykadlainformatykpw','podstawyelektroniki,elektrotechnikiimiernictwa']
I1 = ['wstepdoinformatyki','architekturasystempwkomputerowych','architekturysystempwkomputerowych','bazydanych','systemyoperacyjne','siecikomputerowe','inżynieriaoprogramowania']
Iinz = ['systemywbudowane','podstawygrafikikomputerowej','sztucznainteligencja','komunikacjacz\xa3owiek-komputer']
FEREOL_PATH = '../../..'

SEMESTERID = 330

przedmioty = {
    "ALGEBRA" : 3174,
 "ALGORYTMICZNA TEORIA GIER" :3175 ,
 "ALGORYTMY I STRUKTURY DANYCH (M)" :3178 ,
 "ALGORYTMY ROZPROSZONE": 3180 ,
 "ALGORYTMY W SIECIACH BEZPRZEWODOWYCH I SENSOROWYCH" :3181 ,
 "ANALIZA PROGRAMoW KOMPUTEROWYCH" :3185 ,
 "ARCHITEKTURY SYSTEMoW KOMPUTEROWYCH" :3186 ,
 "BAZY DANYCH" : 3187,
 "BAZY DANYCH (ANG.)": 3188,
 "EKSPLORACJA DANYCH": 3192 ,
 "FIZYKA DLA INFORMATYKoW" : 3194,
 "GEOMETRIA OBLICZENIOWA" : 3195,
 "JeZYKI FORMALNE I ZlOzONOsc OBLICZENIOWA" : 3199,
 "KRYPTOGRAFIA" : 3201,
 "KURS BEZPIECZEnSTWA APLIKACJI W INTERNECIE" : 3203,
 "KURS JeZYKA C++" : 3204,
 "KURS PRACY W SYSTEMIE LINUX" : 3207,
 "KURS PROGRAMOWANIA POD WINDOWS W TECHNOLOGII .NET" : 3209,
 "KURS PROGRAMOWANIA POD WINDOWS W TECHNOLOGII .NET (ANG.)": 3210,
 "KURS: PROGRAMOWANIE W C++" : 3216,
 "KURS XML" : 3214,
 "LICENCJACKI PROJEKT PROGRAMISTYCZNY" : 3218,
 "MATEMATYCZNE METODY GRAFIKI KOMPUTEROWEJ" : 3220,
 "METODY BIOMETRYCZNE" : 3286,
 "METODY PROGRAMOWANIA" : 3173,
 "OPTYMALIZACJA KOMBINATORYCZNA" : 3226,
 "PROGRAMOWANIE OBIEKTOWE" : 3231,
 "PROJEKTOWANIE OBIEKTOWE OPROGRAMOWANIA" : 3234,
 "RACHUNEK PRAWDOPODOBIEnSTWA I STATYSTYKA" : 3236,
 "REALISTYCZNA GRAFIKA KOMPUTEROWA" : 3237,
 "SEMINARIUM: ALGORYTMY FUNKCJONALNE I TRWAlE STRUKTURY DANYCH" : 3241,
 "SEMINARIUM: GRAFIKA KOMPUTEROWA 2014" : 3246,
 "SEMINARIUM: INzYNIERIA OPROGRAMOWANIA" : 3248,
 "SIECI KOMPUTEROWE" : 3257,
 "SYNTEZA MOWY" : 3259,
 "SYSTEMY ROZPROSZONE" : 3261,
 "SZTUCZNA INTELIGENCJA" : 3263,
 "TEORETYCZNE PODSTAWY JeZYKoW PROGRAMOWANIA" : 3264,
 "TESTOWANIE OPROGRAMOWANIA" : 3266,
 "CCNA EXPLORATION 1 (LATO)" : 3190,
 "SEMINARIUM: PODSTAWY JeZYKOW ZORIENTOWANYCH OBIEKTOWO" : 3251,
 "SEMINARIUM: SIECI NEURONOWE I STATYSTYKA" : 3252,
 "PRAKTYCZNE ASPEKTY ROZWOJU OPROGRAMOWANIA" : 3283,
 "KURS: PRACTICAL C ENTERPRISE SOFTWARE DEVELOPMENT": 3282
}


TECH = { "KRYSTIAN BAClAWSKI": 96,
 "MAlGORZATA BIERNACKA":  73,
 "DARIUSZ BIERNACKI":  70,
 "MARCIN BIEnKOWSKI":  11,
 "SZYMON BONIECKI":  73,
 "JAROSlAW BYRKA":  102,
 "WITOLD CHARATONIK":  54,
 "JAN CHOROWSKI":  456,
 "HANS DENIVELLE":  66,
 "KRZYSZTOF DeBICKI":  69,
 "AGNIESZKA FALEnSKA":464,
 "PATRYK FILIPIAK":  107,
 "INSTYTUT FIZYKI DOsWIADCZALNEJ":  178,
 "PRZEMYSlAW GOSPODARCZYK":  449,
 "LESZEK GROCHOLSKI":  13,
 "TOMASZ JURDZInSKI":  16,
 "ADAM KACZMAREK": 457,
 "PRZEMYSlAWA KANAREK": 18,
 "WITOLD KARCZEWSKI": 19,
 "MICHAl KARPInSKI": 463,
 "EMANUEL KIEROnSKI": 22,
 "WOJCIECH KLESZOWSKI": 116,
 "JAKUB KOWALSKI": 109,
 "ANTONI KOsCIELSKI": 24,
 "JURIJ KRYAKIN": 26,
 "ANDRZEJ KRZYWDA":  120,
 "ILONA KRoLAK":  28,
 "STANISlAW LEWANOWICZ":  29,
 "KRZYSZTOF LORYs":  30,
 "JERZY MARCINKOWSKI": 31,
 "MAREK MATERZOK": 92,
 "MARCIN MlOTKOWSKI": 34,
 "RAFAl NOWAK": 35,
 "LESZEK PACHOLSKI":  36,
 "MACIEJ PACUT": 465,
 "KATARZYNA PALUCH":  37,
 "MACIEJ PALUSZYnSKI": 65,
 "WITOLD PALUSZYnSKI": 38,
 "KRZYSZTOF PIECUCH": 460,
 "MAREK PIOTRoW": 39,
 "lUKASZ PIWOWAR": 40,
 "BARTOSZ RYBICKI": 439,
 "ZDZISlAW PlOSKI": 41,
 "PAWEl RAJBA": 53,
 "PAWEl RYCHLIKOWSKI": 42,
 "PAWEl RZECHONEK":  43,
 "MICHAl RozAnSKI": 458,
 "KATARZYNA SERAFInSKA": 461,
 "KRZYSZTOF SORNAT": 459,
 "PAWEl SOlTYSIAK": 91,
 "ZDZISlAW SPlAWSKI": 3,
 "GRZEGORZ STACHOWIAK": 44,
 "DAMIAN STRASZAK": 466,
 "MACIEJ M. SYSlO": 114,
 "ADAM SZUSTALEWICZ": 82,
 "MAREK SZYKUlA": 90,
 "KRZYSZTOF TABISZ": 86,
 "PIOTR WIECZOREK": 48,
 "TOMASZ WIERZBICKI": 49,
 "PIOTR WITKOWSKI": 5,
 "PIOTR WNUK-LIPInSKI":  50,
 "MIECZYSlAW WODECKI": 51,
 "PAWEl WOzNY": 52,
 "WIKTOR ZYCHLA": 7,
 "ANDRZEJ lUKASZEWSKI": 8,
  "ADRIAN lAnCUCKI": 462,
}




####  #####

import sys
import os
from django.core.management import setup_environ
from datetime import time


from apps.enrollment.courses.models import Course, Semester, CourseEntity, Type, Group, Term, PointsOfCourseEntities, PointTypes
from apps.users.models import Student, Employee, Program

from apps.enrollment.courses.models import Classroom

from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db import transaction

from datetime import datetime
import re
import logging
logger = logging.getLogger()


regex = re.compile('\s+(?P<day>pn|wt|sr|czw|pi|so|ni)\s+(?P<start_time>\d{1,2})-(?P<end_time>\d{1,2})\s+\((?P<type>wyklad|repetytorium|cwiczenia|pracownia|cwicz\+pracownia|seminarium)\)\s+(?P<teacher>[^,]*),\s+(?P<rooms>.*)')

GROUP_TYPES = { 'wyklad' : '1', 'repetytorium' : '9', 'cwiczenia' : '2', 'pracownia' : '3' ,'cwicz+pracownia' : '5' ,'seminarium' : '6' }

DAYS_OF_WEEK = { 'pn' : '1', 'wt' : '2', 'sr' : '3', 'czw' : '4', 'pi' : '5' , 'so' : '6', 'ni' : '7'}


def find_teacher(t):
    id = TECH.get(t, None)
    if id:
        return Employee.objects.get(id=id)
    else:
        return None

def get_classroom(rooms):
    classrooms = []
    for room in rooms:
        try:
            if room.replace(' ','')=='':
                classroom = None
            else:
                classroom = Classroom.objects.get(number=room)
        except ObjectDoesNotExist:
            classroom = None
        if classroom:
            classrooms.append(classroom)

    return classrooms


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
    classroom = None

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
                classrooms = get_classroom(rooms)

                group_type = GROUP_TYPES[g.group('type')]
                teacher = find_teacher(g.group('teacher'))
                limit = LIMITS[group_type]
                
                t = 15*(int(g.group('end_time'))-int(g.group('start_time')))
                    
                if group_type=='1':    
                    group = Group.objects.get_or_create(course=course,
                                                        teacher=teacher,
                                                        type=group_type,
                                                        limit=limit)[0]
                else:
                    group = Group.objects.create(course=course,
                                                        teacher=teacher,
                                                        type=group_type,
                                                        limit=limit)
                term = Term.objects.create(dayOfWeek=dayOfWeek,
                                           start_time=start_time,
                                           end_time=end_time,
                                           classroom=classroom,
                                           group=group)
                term.classrooms = classrooms
                term.save()
                
            except AttributeError:
                print 'Error: line`'+line+'\' don\'t match regexp.'

        elif line.startswith(' '):
            if line==' \n':
                continue
            
            name = line[1:-2]
            try:
                course = get_course(name)
            except Exception, e:
                print 'Error during creating course:%s. \nError: %s ' % (name, e)
                break

        else:
            continue

def get_semester():
    return Semester.objects.get(id=SEMESTERID)

def get_course(name):
    return Course.objects.get(id=przedmioty[name])

def run():
    semester = get_semester()
    print 'Przenosimy na semestr <%s>' % semester
    file = open(SCHEDULE_FILE)
    import_schedule(file, semester)

