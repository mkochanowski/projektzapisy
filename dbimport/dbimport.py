# -*- coding: utf-8 -*-

FEREOL_PATH = '../..'

# Old database connection settings:
OLDDB_NAME = ''
OLDDB_USER = ''
OLDDB_PASS = ''
OLDDB_HOST = ''
OLDDB_PORT = ''

import sys
import os
from django.core.management import setup_environ

if __name__ == '__main__':
    sys.path.append(FEREOL_PATH)
    sys.path.append(FEREOL_PATH + '/fereol')
    from fereol import settings
    setup_environ(settings)

import psycopg2 as pg
import psycopg2.extensions

from apps.enrollment.records.models import Record, STATUS_ENROLLED
from apps.enrollment.courses.models import Course, Semester, CourseEntity, Type, Group, Term, Classroom
from apps.users.models import Student, Employee

from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db import transaction

from datetime import datetime

def import_users(conn):
    cur = conn.cursor()
    cur.execute('select imie, nazwisko, email, rok from uzytkownik')

    matricula = 0
    
    for rec in cur:
        if rec[2] is None:
            email = ''
        else:
            email = rec[2]

        name = rec[0]
        surname = rec[1]
        year = rec[3]

        try:
            user = User.objects.get(first_name=name,
                             last_name=surname
                             )

            print '[WARNING] User already exists:', name, surname
            
        except User.DoesNotExist:
            transaction.rollback()
            
            user = User.objects.create(username=matricula,
                                       first_name=name,
                                       last_name=surname,
                                       email=email
                                       )

        if year is None or year == 0:
            Employee.objects.get_or_create(user=user)
        else:
            try:
                Student.objects.get(user=user)
            except Student.DoesNotExist:
                transaction.rollback()
                
                Student.objects.get_or_create(user=user,
                                              matricula=str(matricula)
                                              )

        matricula = matricula + 1;

    cur.close()

def get_user(conn, id):
    cur = conn.cursor()
    cur.execute('select imie, nazwisko from uzytkownik where kod_uz = %s',
                (id,)
                )
    rec = cur.fetchone()

    if rec is None:
        print '[ERROR] uzytkownik.kod_uz =', id, 'does not exist'
        return None
    
    name = rec[0]
    surname = rec[1]

    user = None

    try:
        user = User.objects.get(first_name=name,
                                last_name=surname
                                )
    except:
        print '[ERROR] User does not exist:', name, surname
        transaction.rollback()

    return user

def get_teacher(conn, id):
    user = get_user(conn, id)

    if user is None:
        return None

    employee = None

    try:
        employee = user.employee
    except Employee.DoesNotExist:
        print '[ERROR] User exists but not as employee:', user.first_name, user.last_name
        transaction.rollback()

        print '[INFO] Adding as employee...'

        employee = Employee.objects.create(user=user)
    
    return employee

def get_student(conn, id):
    user = get_user(conn, id)

    if user is None:
        return None

    student = None

    try:
        student = user.student
    except Student.DoesNotExist:
        print '[ERROR] User exists but not as student:', user.first_name, user.last_name        
        transaction.rollback()

    return student

def import_records(conn, gr_id, group):
    cur = conn.cursor()
    cur.execute('select kod_uz from wybor where kod_grupy = %s',
                (gr_id,))

    for rec in cur:
        student_id = rec[0]

        student = get_student(conn, student_id)

        if student is None:
            print '[ERROR] kod_uz =', student_id, 'in wybor does not exist in new db'
            return

        try:
            Record.objects.create(group=group,
                                  student=student,
                                  status=STATUS_ENROLLED
                                  )
        except:
            print '[ERROR] User kod_uz =', student_id, 'and kod_grupy =', gr_id, 'probably exists in Records'
            transaction.rollback()

def import_terms(conn, gr_id, group):
    cur = conn.cursor()
    cur.execute('select termin, sala from plan where kod_grupy = %s',
                (gr_id,))

    hours = 0

    for rec in cur:
        term_txt = rec[0]
        room_txt = rec[1]
        
        day = term_txt[0:1]
        start = term_txt[2:7].replace(' ','0')
        end = term_txt[8:13].replace(' ','0')
        room = Classroom.objects.get_or_create(number=room_txt)[0]

        term = Term.objects.create(dayOfWeek=day,
                                   start_time=start,
                                   end_time=end,
                                   classroom=room,
                                   group=group
                                   )

        if hours == 0:
            hours = (datetime.strptime(end, '%H:%M') - datetime.strptime(start, '%H:%M')).seconds/3600

    return hours

def import_groups(conn, sub_id, sub):
    cur = conn.cursor()
    cur.execute('select kod_grupy, kod_uz, max_osoby, rodzaj_zajec from grupa where kod_przed_sem = %s',
                (sub_id,))

    for rec in cur:
        gr_id = rec[0]
        teacher_id = rec[1]
        limit = rec[2]
        gr_type_id = rec[3]

        teacher = get_teacher(conn, teacher_id)

        if gr_type_id == 'w':
            gr_type = '1'
        elif gr_type_id == 'c':
            gr_type = '2'
        elif gr_type_id == 'p':
            gr_type = '3'
        elif gr_type_id == 'C':
            gr_type = '4'
        elif gr_type_id == 'r':
            gr_type = '5'
        elif gr_type_id == 's':
            gr_type = '6'
        elif gr_type_id == 'l':
            gr_type = '7'
        else:
            print '[ERROR] Group type is not recognized:', gr_type_id
            continue

        group = Group.objects.create(course=sub,
                                     teacher=teacher,
                                     type=gr_type,
                                     limit=limit
                                     )

        hours = import_terms(conn, gr_id, group)*15

        if sub.lectures == 0 and gr_type_id == 'w':
            sub.lectures = hours
            sub.save()
        elif sub.exercises == 0 and gr_type_id == 'c':
            sub.exercises = hours
            sub.save()
        elif sub.laboratories == 0 and gr_type_id == 'p':
            sub.laboratories = hours
            sub.save()
        
        import_records(conn, gr_id, group)

def import_courses(conn, sem_id, sem):
    cur = conn.cursor()
    cur.execute('select kod_przed_sem, nazwa, rodzaj_od_2007, opis, kod_uz, punkty_ects from przedmiot join przedmiot_semestr using(kod_przed) where semestr_id = %s',
                (sem_id,)
                )

    for rec in cur:
        sub_id = rec[0]
        name = rec[1]
        sub_type_id = rec[2]

        if rec[3] is None:
            desc = ''
        else:
            desc = rec[3]

        teacher_id = rec[4]
        ects = rec[5]
            
        entity = CourseEntity.objects.get_or_create(name=name)[0]
        slug = str(sem.year) + sem.type + '_' + slugify(name) # FIXME: slugify removes polish diacritical signs

        if sub_type_id == 1:
            sub_type = Type.objects.get_or_create(name='Obowiązkowy O.1')[0]
        elif sub_type_id == 2:
            sub_type = Type.objects.get_or_create(name='Obowiązkowy O.2')[0]
        elif sub_type_id == 3:
            sub_type = Type.objects.get_or_create(name='Obowiązkowy O.3')[0]
        elif sub_type_id == 4:
            sub_type = Type.objects.get_or_create(name='Informatyczny I.1')[0]
        elif sub_type_id == 5:
            sub_type = Type.objects.get_or_create(name='Informatyczny I.2')[0]
        elif sub_type_id == 6:
            sub_type = Type.objects.get_or_create(name='Kurs')[0]
        elif sub_type_id == 7:
            sub_type = Type.objects.get_or_create(name='Seminarium')[0]
        elif sub_type_id == 8:
            sub_type = Type.objects.get_or_create(name='Nieinformatyczny')[0]
        elif sub_type_id == 9:
            sub_type = Type.objects.get_or_create(name='Nieinformatyczny')[0]
        else:
            print '[ERROR] Type of course', name, 'not recognized:', sub_type_id
            continue

        sub = None

        try:
            sub = Course.objects.create(name=name,
                                         entity=entity,
                                         slug=slug,
                                         semester=sem,
                                         type=sub_type,
                                         ects=ects,
                                         description=desc,
                                         lectures=0,
                                         laboratories=0,
                                         exercises=0
                                         )
        
        except Exception:
            print '[ERROR] Probably field slug not unique:', slug
            transaction.rollback()

        if sub is not None:
            if teacher_id is not None:
                teacher = get_teacher(conn, teacher_id)

                if teacher is not None:
                    sub.teachers = [teacher]
                    sub.save()

            import_groups(conn, sub_id, sub)

    cur.close()
    
def import_semesters(conn):
    cur = conn.cursor()
    cur.execute('select id_semestr, nazwa from semestr')

    for rec in cur:
        print '[INFO] Importing semester:', rec[1]
        
        if len(rec[1]) <= 24 and rec[1][8:13] == 'letni':
            sem_type = Semester.TYPE_SUMMER
            year = int(rec[1][14:18])
        elif len(rec[1]) <= 24 and  rec[1][8:14] == 'zimowy':
            sem_type = Semester.TYPE_WINTER
            year = int(rec[1][15:19])
        else:
            print '[WARNING] Semester not imported:', rec[1]
            continue

        try:
            sem = Semester.objects.create(type=sem_type,
                                          year=year,
                                          visible=True
                                          )
        except:
            print '[ERROR] Semester probably exists:', rec[1]
            transaction.rollback()
            continue

        import_courses(conn, rec[0], sem)

    cur.close()

@transaction.autocommit
def importdb():    
    conn = pg.connect('dbname=%s user=%s password=%s host=%s port=%s' \
                      % (OLDDB_NAME, OLDDB_USER, OLDDB_PASS, OLDDB_HOST, OLDDB_PORT) \
                      )

    print '[INFO] Database encoding:', conn.encoding

    import_users(conn)
    import_semesters(conn)

    conn.close()
    
if __name__ == '__main__':
    importdb()
