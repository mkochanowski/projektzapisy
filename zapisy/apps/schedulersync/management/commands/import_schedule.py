# -*- coding: utf-8 -*-
import re
import logging
from datetime import time
from sets import Set

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.users.models import Student, Employee, Program
from apps.enrollment.courses.models import Classroom
from apps.enrollment.courses.models import (
    Course, Semester, CourseEntity,
    Type, Group, Term, PointsOfCourseEntities, PointTypes
)
from apps.schedulersync.models import TermSyncData

import requests
import json

LIMITS = {'1': 300, '9': 300, '2': 20, '3': 15, '5': 18, '6': 15}
GROUP_TYPES = {'w': '1', 'e': '9', 'c': '2', 'p': '3',
               'r': '5', 's': '6'}

employee_map = {
    'PWL': u'PWN',
    'MBI': u'MBIEŃKOWSKI',
    'KBACLAWSKI': u'KBACŁAWSKI',
    'MABI': u'MBIERNACKA',
    'PWI': u'48',
    'IFD': u'IDO',
    'JMA': u'31',
    'ANL': u'AŁU',
    'PAWIECZOREK': u'526',
    'LPI': u'ŁPI',
    'DABI': u'DBIERNACKI',
    'MPIROG': u'MPIRÓG',
    'WKWASNICKI': u'WKWAŚNICKI',
    'ASIERON': u'ASIEROŃ',
    'ZPLOSKI': u'ZPŁOSKI',
    'ZSPLAWSKI': u'ZSPŁAWSKI',
    'PACHOLSKI LESZEK': u'LPA',
    'MML': u'MMŁ',
    'LJE': u'ŁJE',
    'MPI': u'MPIOTRÓW'
}

courses_map = {
    u'ALGORYTMY I STRUKTURY DANYCH M': u'ALGORYTMY I STRUKTURY DANYCH (M)',
    u'KURS PHP': u'Kurs: Projektowanie i implementacja zaawansowanych aplikacji PHP',
    u'PROJEKT DYPLOMOWY (LATO)': u'PROJEKT DYPLOMOWY',
    u'PROJEKT: SYSTEM ZAPISÓW (LATO)': u'PROJEKT: ROZWÓJ SYSTEMU ZAPISÓW',
    u'PROJEKT ZESPOŁOWY: SILNIK UNITY3D I WIRTUALNA RZECZYWISTOŚĆ 2':
        u'Projekt zespołowy: silnik Unity3D i wirtualna rzeczywistość LATO',
    u'SEMINARIUM: ALGORYTMY  WYSZUKIWANIA ŚCIEŻEK': u'SEMINARIUM: ALGORYTMY WYSZUKIWANIA ŚCIEŻEK',
    u'TUTORING (LATO)': u'Kształtowanie ścieżki akademicko-zawodowej'
}

courses_dont_import = [u'XIV LO LATO', u'ZASADY KRYTYCZNEGO MYŚLENIA']


class Command(BaseCommand):
    args = ''
    help = 'Imports the timetable for the next semester from the external scheduler.'

    def add_arguments(self, parser):
        parser.add_argument('-semester', type=int, default=0)
        parser.add_argument('-create_courses', action='store_true', dest='create_courses')
        parser.add_argument('-dry_run', action='store_true', dest='dry_run')

    def get_entity(self, name):
        name = name.upper()
        if name in courses_map:
            name = courses_map[name]
        if name in courses_dont_import:
            return None
        ce = None
        try:
            ce = CourseEntity.objects.get(name_pl__iexact=name)
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(u">Couldn't find course entity for "
                                               + name.decode('utf-8')))
        except MultipleObjectsReturned:
            if self.verbosity >= 1:
                self.stdout.write(self.style.WARNING('Multiple course entity'))
                ces = CourseEntity.objects.filter(name_pl__iexact=name, status=2).order_by('-id')
                for ce in ces:
                    self.stdout.write(self.style.WARNING('  '+str(ce).decode('utf-8')))
                self.stdout.write('')
            ce = ces[0]
        return ce

    def get_course(self, entity, create_courses=False):
        course = None
        try:
            course = Course.objects.get(semester=self.semester, entity=entity)
            self.used_courses.add(course)
        except ObjectDoesNotExist:
            if entity.slug is None:
                self.stdout.write(self.style.ERROR(u"Couldn't find slug for "
                                                   + str(entity).decode('utf-8')))
            else:
                newslug = entity.slug + '_' + \
                          self.semester.get_short_name().replace(' ', '_').replace('/', '_')
                if create_courses:
                    course = Course(entity=entity, information=entity.information,
                                    semester=self.semester, slug=newslug)
                    course.save()
                    self.created_courses += 1
        return course

    def get_classrooms(self, rooms):
        classrooms = []
        for room in rooms:
            try:
                if room.replace(' ', '') == '':
                    classroom = None
                else:
                    classroom = Classroom.objects.get(number=room)
            except ObjectDoesNotExist:
                classroom = None
                self.stdout.write(self.style.ERROR(u"Couldn't find classroom for "
                                  + room.decode('utf-8')))
            if classroom:
                classrooms.append(classroom)
        return classrooms

    def get_employee(self, name):
        name = name.upper()
        if name in employee_map:
            name = employee_map[name]
        try:
            int(name)
            emps = Employee.objects.filter(id=name)
        except ValueError:
            if name == 'NN':
                emps = Employee.objects.filter(user__first_name='Nieznany')
            elif len(name) == 3:
                emps = Employee.objects.filter(user__first_name__istartswith=(
                                               name[0]),
                                               user__last_name__istartswith=(
                                               name[1:3]),
                                               status=0)
            else:
                emps = Employee.objects.filter(user__first_name__istartswith=(
                                               name[0]),
                                               user__last_name__istartswith=(
                                               name[1:]),
                                               status=0)
        if len(emps) == 1:
            return emps[0]
        elif len(emps) > 1:
            self.stdout.write(self.style.ERROR(u"Multiple employee matches for "
                              + name+". Choices are:"))
            for e in emps:
                self.stdout.write(self.style.ERROR("  -"+e.user.get_full_name()))
        else:
            raise CommandError('Employee %s does not exists! Fix your input file.' % name)

        return None

    def create_or_update_group(self, course, data):
        try:
            sync_data_object = TermSyncData.objects.get(scheduler_id=data['id'])
            term = sync_data_object.term
        except ObjectDoesNotExist:
            # Create the group in the enrollment system
            if data['group_type'] == '1':
                # The lecture always has a single group but possibly many terms
                group = Group.objects.get_or_create(course=course,
                                                    teacher=data['teacher'],
                                                    type=data['group_type'],
                                                    limit=data['limit'])[0]
            else:
                group = Group.objects.create(course=course,
                                             teacher=data['teacher'],
                                             type=data['group_type'],
                                             limit=data['limit'])
            term = Term.objects.create(dayOfWeek=data['dayOfWeek'],
                                       start_time=data['start_time'],
                                       end_time=data['end_time'],
                                       group=group)
            term.classrooms = data['classrooms']
            term.save()
            TermSyncData.objects.create(term=term, scheduler_id=data['id'])
            self.created_terms += 1
        else:
            diff_track_fields = ['dayOfWeek', 'start_time', 'end_time']
            diffs = [(k, (getattr(term, k), data[k])) for k in diff_track_fields
                     if getattr(term, k) != data[k]]
            if term.group.type != data['group_type']:
                diffs.append(('type', (term.group.type, data['group_type'])))
            if term.group.teacher != data['teacher']:
                diffs.append(('teacher', (term.group.teacher, data['teacher'])))
            term.dayOfWeek = data['dayOfWeek']
            term.start_time = data['start_time']
            term.end_time = data['end_time']
            term.group.type = data['group_type']
            term.group.teacher = data['teacher']
            if len(diffs) > 0:
                term.save()
                term.group.save()
                self.stdout.write(self.style.SUCCESS('Group updated: ' +
                                  str(term.group).decode('utf-8') + ' ' +
                                  str(term).decode('utf-8') +
                                  '\n  ' + str(diffs).decode('utf-8') + '\n'))
                self.updated_terms += 1

    def prepare_group(self, g, results, terms):
        group = {}
        group['id'] = g['id']
        group['entity_name'] = g['extra']['course']
        group['group_type'] = GROUP_TYPES[g['extra']['group_type']]
        group['teacher'] = self.get_employee(g['teachers'][0])
        start_time = 20
        end_time = 0
        classrooms = Set()
        if g['id'] in results:
            for t in results[g['id']]:
                t_start = terms[t['term']]['start']['hour']
                t_end = terms[t['term']]['end']['hour']
                if t_start < start_time:
                    start_time = t_start
                if t_end > end_time:
                    end_time = t_end
                group['dayOfWeek'] = str(terms[t['term']]['day']+1)
                classrooms.add(t['room'])
            group['start_time'] = time(hour=int(start_time))
            group['end_time'] = time(hour=int(end_time))
            group['classrooms'] = self.get_classrooms(list(classrooms))
            group['limit'] = LIMITS[group['group_type']]
            return group
        else:
            return None

    def get_groups(self):
        url = ('http://scheduler.gtch.eu/admin/login/')
        client = requests.session()
        client.get(url)
        csrftoken = client.cookies['csrftoken']
        login_data = {'username': 'test', 'password': 'test', 'csrfmiddlewaretoken': csrftoken,
                      'next': '/scheduler/api/config/2017-18-lato3-2/'}
        r = client.post(url, data=login_data)
        r2 = client.get('http://scheduler.gtch.eu/'
                        'scheduler/api/task/07164b02-de37-4ddc-b81b-ddedab533fec/')
        results = r2.json()['timetable']['results']
        groups = []
        terms = {}
        data = r.json()
        for t in data['terms']:
            terms[t['id']] = t
        for g in data['groups']:
            prepared_group = self.prepare_group(g, results, terms)
            if prepared_group is not None:
                groups.append(prepared_group)
            else:
                self.stdout.write(self.style.WARNING('Group number {} does not have a term ({})\n'
                                  .format(g['id'], g['extra']['course'])))
        return groups

    @transaction.atomic
    def import_from_api(self, create_courses=False, create_terms=True):
        self.created_terms = 0
        self.updated_terms = 0
        self.created_courses = 0
        self.used_courses = Set()
        groups = self.get_groups()
        for g in groups:
            entity = self.get_entity(g['entity_name'])
            if entity is not None:
                course = self.get_course(entity, create_courses)
                if course is None:
                    raise CommandError('Course does not exists! Check your input file.')
                if create_terms:
                    self.create_or_update_group(course, g)
        self.stdout.write(self.style.SUCCESS('Created {} courses successfully! '
                                             'Moreover {} courses was already there.'
                          .format(self.created_courses, len(self.used_courses))))
        self.stdout.write(self.style.SUCCESS('Created {} terms and updated {} terms successfully!'
                          .format(self.created_terms, self.updated_terms)))

    def handle(self, *args, **options):
        self.semester = None
        if options['semester'] == 0:
            self.semester = Semester.objects.get_next()
        else:
            self.semester = Semester.objects.get(pk=int(options['semester']))
        self.verbosity = options['verbosity']
        if self.verbosity >= 1:
            self.stdout.write('Adding to semester: '+str(self.semester)+'\n')
        if options['dry_run']:
            self.import_from_api(False, False)
        else:
            self.import_from_api(options['create_courses'])
