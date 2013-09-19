# -*- coding: utf-8 -*-
"""
DZIA\xa3ANIE
=========
Importuje plan zajeć do nowo stworzonego semestru z pliku .txt z sekretariatu.


CO NALEŻY WIEDZIEĆ
==================
- semestr powstaje z daty dzisiejszej; jeżeli w systemie już taki semestr jest, należy usunąć (wraz z przedmiotami)
- pusta linia na początku pliku powinna być
- jeżeli typy źle sie importują (np. nie ma tych w O1), to:
    . skopiuj plik do justpaste.it
    . kliknij udostepniany link 
    . skopiuj z przeglądarki z powrotem do pliku nowego
    . spróbuj zimportować ten plik, mi pomog\xa3o

CO POPRAWIAĆ PO IMPORCIE
========================
- przedmioty, które potencjalnie mają z\xa3y typ, są w Informatyczny 2
- punkty dla przedmiotów L/M
- niepolskie nazwiska
- wyk\xa3ady posiadające dwa terminy trzeba zmergować

URUCHAMIANIE
============
Z panelu admina:
wejdź w /fereol_admin/courses i kliknij importowanie planu zajeć z sekretariatu.

Jeżeli chcesz importować z konsoli, a nie z panelu admina, odkomentuj:
#scheduleimport('')
#file = open(SCHEDULE_FILE)
i zakomentuj
file = data.

Uruchomienie:
$ python scheduleimport.py


"""
#### TO CHANGE #####
SCHEDULE_FILE = 'plan.txt'
LIMITS = {'1' : 300, '9' : 300, '2' : 20, '3' : 15 , '5' : 18 , '6' : 15 }

FIRST_YEAR_FRIENDLY = ['logikadlainformatyków','analizamatematyczna','algebra','kursjezykaansiczelementamic++','wstepdoinformatyki',
                       'wstepdoprogramowania','programowanie','programowanieobiektowe','kursjezykapascal',
                       'architekturysystemówkomputerowych', 'architekturasystemówkomputerowych']
O1 = ['analizamatematyczna','algebra','logikadlainformatyków','elementyrachunkuprawdopodobieństwa','metodyprobabilistyczneistatystyka']
O2 = ['matematykadyskretna','programowanie','analizanumeryczna','algorytmyistrukturydanych']
O3 = ['jezykiformalneiz\xa3ożonosćobliczeniowa']
Oinz = ['fizykadlainformatyków','podstawyelektroniki,elektrotechnikiimiernictwa']
I1 = ['wstepdoinformatyki','architekturasystemówkomputerowych','architekturysystemówkomputerowych','bazydanych','systemyoperacyjne','siecikomputerowe','inżynieriaoprogramowania']
Iinz = ['systemywbudowane','podstawygrafikikomputerowej','sztucznainteligencja','komunikacjacz\xa3owiek-komputer']
FEREOL_PATH = '../../..'

SEMESTERID = 329

przedmioty = { "ALGORYTMY EWOLUCYJNE": 3176,
 "ALGORYTMY FUNKCJONALNE I TRWAlE STRUKTURY DANYCH": 3177,
 "ALGORYTMY INTERNETU": 3179,
 "ANALIZA MATEMATYCZNA": 3182,
 "ANALIZA NUMERYCZNA (L)": 3183,
 "ANALIZA NUMERYCZNA (M)": 3184,
 "COMPILER CONSTRUCTION": 3191,
 "INTEGRACJA INFORMACJI": 3196,
 "INzYNIERIA OPROGRAMOWANIA": 3197,
 "KOMUNIKACJA CZlOWIEK-KOMPUTER": 3200,
 "KULTURA BEZPIECZEnSTWA KOMPUTEROWEGO": 3202,
 "KURS JeZYKA JAVA": 3205,
 "KURS: PROCESORY GRAFICZNE W OBLICZENIACH RoWNOLEGlYCH (CUDA)": 3215,
 "KURS PROGRAMOWANIA APLIKACJI BAZODANOWYCH": 3208,
 "KURS PROJEKTOWANIA APLIKACJI ASP.NET I SILVERLIGHT": 3211,
 "KURS ROZSZERZONY JeZYKA PYTHON": 3212,
 "KURS: RUBY ON RAILS": 3217,
 "KURS WWW": 3213,
 "LOGIKA DLA INFORMATYKoW": 3219,
 "MATEMATYKA DYSKRETNA (L)": 3221,
 "MATEMATYKA DYSKRETNA (M)": 3222,
 "METODY OPTYMALIZACJI": 3224,
 "MODELOWANIE ZJAWISK PRZYRODNICZYCH": 3225,
 "PODSTAWY ELEKTRONIKI, ELEKTROTECHNIKI I MIERNICTWA": 3228,
 "PODSTAWY GRAFIKI KOMPUTEROWEJ": 3229,
 "PROGRAMOWANIE FUNKCYJNE": 3230,
 "PROJEKT ZESPOlOWY": 3233,
 "RACHUNEK PRAWDOPODOBIEnSTWA DLA INFORMATYKoW": 3235,
 "SEMANTYKA JeZYKoW PROGRAMOWANIA": 3238,
 "SEMINARIUM ALGORYTMICZNE 2014": 3239,
 "SEMINARIUM: ALGORYTMY PROBABILISTYCZNE": 3224,
 "SEMINARIUM APROKSYMACYJNO-OPTYMALIZACYJNO-KOMBINATORYCZNE 2013/2014": 3240,
 "SEMINARIUM: BEZPIECZEnSTWO I OCHRONA INFORMACJI": 3244,
 "SEMINARIUM: DATA-MINING - KLASYFIKACJA I GRUPOWANIE DANYCH": 3245,
 "SEMINARIUM: LOGIKI NIEKLASYCZNE: TEORIA I ZASTOSOWANIA": 3249,
 "SEMINARIUM: TEXT MINING": 3253,
 "SEMINARIUM: ZAAWANSOWANE PROGRAMOWANIE FUNKCYJNE": 3254,
 "SEMINARIUM: ZAAWANSOWANE TECHNIKI PROGRAMOWANIA .NET": 3255,
 "SEMINARIUM: ZAGADKI TEORETYCZNYCH PODSTAW BAZ DANYCH": 3256,
 "SYSTEMY OPERACYJNE": 3260,
 "SYSTEMY WBUDOWANE": 3262,
 "ZlOzONOsc OBLICZENIOWA": 3268,
 "CCNA EXPLORATION 1 (ZIMA)": 3189,
 "ELEMENTY RACHUNKU PRAWDOPODOBIEnSTWA (ANG.)": 3193,
 "INzYNIERIA OPROGRAMOWANIA (ANG.)": 3198,
 "KURS JeZYKA JAVA (ANG.)": 3206,
 "KURS: WSTeP DO PROGRAMOWANIA W JeZYKU C": 3269,
 "KURS: WSTeP DO PROGRAMOWANIA W JeZYKU PYTHON": 3270,
 "METODY SZTUCZNEJ INTELIGENCJI W ZARZADZANIU I STEROWANIU PRODUKCJA": 3244,
 "SEMINARIUM: ARCHITEKTURY SYSTEMoW KOMPUTEROWYCH (ANG.)": 3243,
 "SEMINARIUM: METODY IMPLEMENTACJI ALGORYTMoW": 3250,
 "SIECI NEURONOWE": 3258,
 "SZTUCZNA INTELIGENCJA (ANG.)": 3265,
 "WSTeP DO INFORMATYKI": 3267}


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
 "PATRYK FILIPIAK":  107,
 "INSTYTUT FIZYKI DOsWIADCZALNEJ":  178,
 "PRZEMYSlAW GOSPODARCZYK":  449,
 "LESZEK GROCHOLSKI":  13,
 "TOMASZ JURDZInSKI":  16,
 "ADAM KACZMAREK": 457,
 "PRZEMYSlAWA KANAREK": 18,
 "WITOLD KARCZEWSKI": 19,
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
 "KATARZYNA PALUCH":  37,
 "MACIEJ PALUSZYnSKI": 65,
 "WITOLD PALUSZYnSKI": 38,
 "KRZYSZTOF PIECUCH": 460,
 "MAREK PIOTRoW": 39,
 "lUKASZ PIWOWAR": 40,
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
 "ANDRZEJ lUKASZEWSKI": 8}




####  #####

import sys
import os
from django.core.management import setup_environ
from datetime import time


from zapisy.apps.enrollment.courses.models import Course, Semester, CourseEntity, Type, Group, Term, PointsOfCourseEntities, PointTypes
from zapisy.apps.users.models import Student, Employee, Program

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
                classroom = Classroom.objects.get_or_create(number=room)[0]
        except IndexError:
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
    classroom = Classroom.objects.get_or_create(number=0)[0]
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

        else:
            continue

def get_semester():
    return Semester.objects.get(id=SEMESTERID)

def get_course(name):
    return Course.objects.get(id=przedmioty[name])

@transaction.commit_on_success
def scheduleimport(data):
    semester = get_semester()
    print 'Przenosimy na semestr <%s>' % semester
    file = open(SCHEDULE_FILE)
    import_schedule(file, semester)

#scheduleimport('')

if __name__ == '__main__':
    sys.path.append(FEREOL_PATH)
    sys.path.append(FEREOL_PATH + '/zapisy')
    from zapisy import settings
    setup_environ(settings)
    scheduleimport()    

