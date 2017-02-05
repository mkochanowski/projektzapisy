# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student, Program
from sets import Set

IMPORT_FILE = 'tmp_data/export_usos_to_sz_20170114_2208.csv'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def deactivate_all():
    students = Student.objects.all()
    for s in students:
        s.status = 1
        s.save()

programs = set([])

def import_ects(file):
    for line in file:
        process(line)
    print 'Używane programy:'
    print programs

def process(line):
    line = line.strip()
    indeks,imie,nazwisko,email,bk_email,ects,program,etap,aisdL,numerycznaL,dyskretnaL = line.split('|')
    
    if indeks == 'indeks':
        return
    
    ects = int(ects)
    programs.add(program)
    try:
        student = Student.objects.get(matricula=indeks)
    except ObjectDoesNotExist:
        print bcolors.FAIL + "***" + str(indeks) + " brak " + str(ects) + bcolors.ENDC
        return

    student.status = 0
    student.isim = False

    if program == 'INF-K-S1':
        student.program = Program.objects.get(name='Informatyka, dzienne I stopnia')
    elif program == 'ISIM-K-S1':
        student.program = Program.objects.get(name='Informatyka, dzienne I stopnia')
        student.isim = True
    elif program == 'INF-K-2S1':
        student.program = Program.objects.get(name='Informatyka, dzienne I stopnia inżynierskie')
    elif program == 'INF-K-S2':
        student.program = Program.objects.get(name='Informatyka, dzienne II stopnia')
    elif program == 'INF-K-1S2':
        student.program = Program.objects.get(name='Informatyka, dzienne II stopnia inżynierskie')
    else:
        print bcolors.FAIL + "***" + str(indeks) + " brak programu: " + program + bcolors.ENDC
        return

    student.semestr = int(etap[-1])
    

    aisdL = int(aisdL)
    numerycznaL = int(numerycznaL)
    dyskretnaL = int(dyskretnaL)

    if aisdL > 0:
        student.algorytmy_l = True
    if numerycznaL > 0:
        student.numeryczna_l = True
    if dyskretnaL > 0:
        student.dyskretna_l = True


    if student.ects > ects:
        print bcolors.WARNING
    print str((student, student.ects, ects, student.semestr)) + bcolors.ENDC

    student.save()


def run():
    deactivate_all()
    file = open(IMPORT_FILE)
    import_ects(file)