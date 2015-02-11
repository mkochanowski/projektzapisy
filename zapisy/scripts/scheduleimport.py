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

SEMESTERID = 332

przedmioty = {  "SEMINARIUM: STRUKTURY KOMBINATORYCZNE": 3297,
 "KURS: WSTeP DO PROGRAMOWANIA W JeZYKU PYTHON": 3298,
 "RYNKI FINANSOWE": 3299,
 "ANALIZA NUMERYCZNA (M)": 3300,
 "SYSTEMY OPERACYJNE": 3301,
 "WSTeP DO INFORMATYKI": 3302,
 "KURS JeZYKA JAVA": 3303,
 "KURS: RUBY ON RAILS": 3304,
 "LOGIKA DLA INFORMATYKoW": 3305,
 "PODSTAWY GRAFIKI KOMPUTEROWEJ": 3306,
 "MATEMATYKA DYSKRETNA (M)": 3307,
 "PROGRAMOWANIE FUNKCYJNE": 3308,
 "PROJEKT ZESPOlOWY": 3309,
 "MATEMATYKA DYSKRETNA (L)": 3310,
 "PODSTAWY ELEKTRONIKI, ELEKTROTECHNIKI I MIERNICTWA": 3311,
 "RACHUNEK PRAWDOPODOBIEnSTWA DLA INFORMATYKoW": 3312,
 "SEMINARIUM: BEZPIECZEnSTWO I OCHRONA INFORMACJI": 3313,
 "SEMINARIUM: ARCHITEKTURY SYSTEMoW KOMPUTEROWYCH": 3314,
 "KURS PROJEKTOWANIA APLIKACJI ASP.NET": 3315,
 "SEMINARIUM: ZAAWANSOWANE TECHNIKI PROGRAMOWANIA .NET": 3316,
 "SEMINARIUM: INTELIGENTNE SYSTEMY W ZARZaDZANIU: TEORIA I PRAKTYKA": 3317,
 "SYSTEMY WBUDOWANE": 3318,
 "SEMINARIUM APROKSYMACYJNO-OPTYMALIZACYJNO-KOMBINATORYCZNE 2014/2015": 3319,
 "PODSTAWY JeZYKoW PROGRAMOWANIA W SYSTEMIE COQ": 3320,
 "ALGORYTMY EWOLUCYJNE": 3321,
 "KURS JeZYKA RUBY": 3322,
 "KURS: METODYKI ZWINNE WYTWARZANIA OPROGRAMOWANIA": 3342,
 "KURS WWW": 3341,
 "MATEMATYCZNE PODSTAWY INFORMATYKI": 3340,
 "PRAKTYKA OPTYMALIZACJI": 3339,
 "SEMINARIUM: METODY IMPLEMENTACJI ALGORYTMoW": 3338,
 "SEMINARIUM: ROZPOZNAWANIE OBIEKToW 3D": 3337,
 "SIECI NEURONOWE": 3336,
 "ALGORYTMY FUNKCJONALNE I TRWAlE STRUKTURY DANYCH": 3335,
 "PROJEKT: SYNTEZA I ANALIZA MOWY": 3334,
 "FLIGHT SIMULATION": 3333,
 "ALGORYTMY TEKSTOWE": 3332,
 "ANALIZA NUMERYCZNA (L)": 3331,
 "ALGORYTMY ONLINE": 3330,
 "KOMBINATORYKA": 3329,
 "INzYNIERIA OPROGRAMOWANIA": 3328,
 "ANALIZA MATEMATYCZNA": 3327,
 "KOMUNIKACJA CZlOWIEK-KOMPUTER": 3326,
 "KULTURA BEZPIECZEnSTWA KOMPUTEROWEGO": 3325,
 "KURS: WSTeP DO PROGRAMOWANIA W JeZYKU C": 3324,
 "SEMINARIUM: ZAAWANSOWANA ALGORYTMIKA": 3323,
 "KURS PRACTICAL C# ENTERPRISE SOFTWARE DEVELOPMENT": 3343,
 "BAZY DANYCH": 3346,
 "ARCHITEKTURY SYSTEMoW KOMPUTEROWYCH": 3347,
 "SIECI KOMPUTEROWE": 3348,
 "SEMINARIUM: ALGORYTMY NUMERYCZNE": 3349,
 "SEMINARIUM: TESTOWANIE OPROGRAMOWANIA": 3350,
 "SEMINARIUM: SIECI NEURONOWE I STATYSTYKA": 3351,
 "PODSTAWY EKONOMII": 3352,
 "KURS: PROGRAMOWANIE W C++": 3353,
 "PEWNE ALGORYTMY SYMBOLICZNE": 3354,
 "PROGRAMOWANIE OBIEKTOWE": 3355,
 "KURS J ZYKA C++": 3356,
 "METODY BIOMETRYCZNE": 3357,
 "METODY SZTUCZNEJ INTELIGENCJI W ZARZaDZANIU I STEROWANIU PRODUKCJa": 3358,
 "LICENCJACKI PROJEKT PROGRAMISTYCZNY": 3359,
 "RACHUNEK PRAWDOPODOBIEnSTWA I STATYSTYKA": 3360,
 "SEMINARIUM: INzYNIERIA OPROGRAMOWANIA": 3361,
 "TESTOWANIE OPROGRAMOWANIA": 3362,
 "SEMINARIUM Z SYSTEMoW": 3363,
 "SZTUCZNA INTELIGENCJA": 3364,
 "WERYFIKACJA WSPOMAGANA KOMPUTEROWO": 3365,
 "TEORIA GRAFoW": 3366,
 "SEMINARIUM: ZAGADKI TEORETYCZNYCH PODSTAW BAZ DANYCH": 3367,
 "PROJEKTOWANIE OBIEKTOWE OPROGRAMOWANIA": 3368,
 "KURS: NOWOCZESNE J ZYKI PRZETWARZANIA DANYCH: PYTHON, R I MATLAB": 3369,
 "KURS PROGRAMOWANIA POD WINDOWS W TECHNOLOGII .NET": 3370,
 "ALGEBRA": 3371,
 "ALGORYTMY PROBABILISTYCZNE": 3372,
 "ALGORYTMY APROKSYMACYJNE": 3373,
 "KURS PRACY W SYSTEMIE LINUX": 3374,
 "PRZETWARZANIE OBRAZoW": 3375,
 "SEMINARIUM: ZAAWANSOWANE PROGRAMOWANIE FUNKCYJNE": 3376,
 "WNIOSKOWANIE STATYSTYCZNE": 3377,
 "WST P DO RACHUNKU LAMBDA": 3378,
 "ZASTOSOWANIE TEORII KATEGORII DO KONSTRUOWANIA PROGRAMoW": 3379,
 "XML I BAZY DANYCH": 3380,
 "KURS MODELOWANIA 3D I WIZUALIZACJI W PROGRAMIE SKETCHUP": 3381,
 "ZlOzONOsc OBLICZENIOWA": 3392,
 "ALGORYTMY I STRUKTURY DANYCH (M)": 3383,
 "FIZYKA DLA INFORMATYKoW": 3384,
 "ANALIZA MATEMATYCZNA 2": 3385,
 "KURS PROJEKTOWANIA APLIKACJI Z BAZAMI DANYCH": 3393,
 "METODY PROGRAMOWANIA": 3386,
 "PROGRAMOWANIE LOGICZNE": 3387,
 "SEMINARIUM ALGORYTMICZNE 2014": 3388,
 "TEORIA PROGRAMOWANIA LINIOWEGO I CAlKOWITOLICZBOWEGO": 3389,
 "KRYPTOGRAFIA": 3390,
 "KOMPRESJA DANYCH": 3391,

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
  "ROMAN URBAN": 4,
  "BARTOSZ TROJAN": 87,
  "PAWEl LASKOs-GRABOWSKI": 481,
  "ARTUR JEz": 15,
  "URSZULA BANASZCZAK-SOROKA": 478,
 "PATIK GHOSAL": 486,
 "GABRIELA PRZESlAWSKA": 479
}




####  #####

import sys
import os
from django.core.management import setup_environ
from datetime import time


from apps.enrollment.courses.models import Course, Semester, CourseEntity, Type, Group, Term, PointsOfCourseEntities, PointTypes
from apps.users.models import Student, Employee, Program

from apps.enrollment.courses.models import Classroom

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
        print line
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
            
            name = line.strip()
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

