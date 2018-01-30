# -*- coding: utf-8 -*-
import re
from datetime import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import requests

from apps.users.models import Employee
from apps.enrollment.courses.models import (
    Classroom, Course, Semester, CourseEntity, Group, Term
)
from apps.schedulersync.models import TermSyncData

URL_LOGIN = 'http://scheduler.gtch.eu/admin/login/'
URL_ASSIGNMENTS = '/scheduler/api/config/2017-18-lato3-2/'
URL_SCHEDULE = 'http://scheduler.gtch.eu/scheduler/api/task/07164b02-de37-4ddc-b81b-ddedab533fec/'

LIMITS = {'1': 300, '9': 300, '2': 20, '3': 15, '5': 18, '6': 15}
GROUP_TYPES = {'w': '1', 'e': '9', 'c': '2', 'p': '3',
               'r': '5', 's': '6'}

EMPLOYEE_MAP = {
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
    'MPI': u'MPIOTRÓW',
    'SZDUDYCZ': u'SDUDYCZ',
    'MSZYKULA': u'MSZYKUŁA'
}

COURSES_MAP = {
    u'ALGORYTMY I STRUKTURY DANYCH M': u'ALGORYTMY I STRUKTURY DANYCH (M)',
    u'KURS PHP': u'Kurs: Projektowanie i implementacja zaawansowanych aplikacji PHP',
    u'PROJEKT DYPLOMOWY (LATO)': u'PROJEKT DYPLOMOWY',
    u'PROJEKT: SYSTEM ZAPISÓW (LATO)': u'PROJEKT: ROZWÓJ SYSTEMU ZAPISÓW',
    u'PROJEKT ZESPOŁOWY: SILNIK UNITY3D I WIRTUALNA RZECZYWISTOŚĆ 2':
        u'Projekt zespołowy: silnik Unity3D i wirtualna rzeczywistość LATO',
    u'SEMINARIUM: ALGORYTMY  WYSZUKIWANIA ŚCIEŻEK': u'SEMINARIUM: ALGORYTMY WYSZUKIWANIA ŚCIEŻEK',
    u'TUTORING (LATO)': u'Kształtowanie ścieżki akademicko-zawodowej'
}

COURSES_DONT_IMPORT = [u'XIV LO LATO', u'ZASADY KRYTYCZNEGO MYŚLENIA']


class Command(BaseCommand):
    help = 'Imports the timetable for the next semester from the external scheduler.'

    def add_arguments(self, parser):
        parser.add_argument('-semester', type=int, default=0)
        parser.add_argument('--create_courses', action='store_true', dest='create_courses')
        parser.add_argument('--dry-run', action='store_true', dest='dry_run')

    def get_entity(self, name):
        name = name.upper()
        if name in COURSES_MAP:
            name = COURSES_MAP[name]
        if name in COURSES_DONT_IMPORT:
            return None
        ce = None
        try:
            ce = CourseEntity.objects.get(name_pl__iexact=name)
        except CourseEntity.DoesNotExist:
            self.stdout.write(self.style.ERROR(u">Couldn't find course entity for {}"
                                               .format(name.decode('utf-8'))))
        except CourseEntity.MultipleObjectsReturned:
            ces = CourseEntity.objects.filter(name_pl__iexact=name, status=2).order_by('-id')
            if self.verbosity >= 1:
                self.stdout.write(self.style.WARNING(u'Multiple course entity. Took first among:'))
                for ce in ces:
                    self.stdout.write(self.style.WARNING(u'  {}'.format(str(ce).decode('utf-8'))))
                self.stdout.write('')
            ce = ces[0]
        return ce

    def get_course(self, entity, create_courses=False):
        course = None
        try:
            course = Course.objects.get(semester=self.semester, entity=entity)
            self.used_courses.add(course)
        except Course.DoesNotExist:
            if entity.slug is None:
                self.stdout.write(self.style.ERROR(u"Couldn't find slug for {}"
                                                   .format(str(entity).decode('utf-8'))))
            else:
                newslug = '{}_{}'.format(entity.slug,
                                         re.sub(r'[^\w]', '_', self.semester.get_short_name()))
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
                if room.replace(' ', '') != '':
                    classrooms.append(Classroom.objects.get(number=room))
            except Classroom.DoesNotExist:
                self.stdout.write(self.style.ERROR(u"Couldn't find classroom for {}"
                                                   .format(room.decode('utf-8'))))
        return classrooms

    def get_employee(self, name):
        name = name.upper()
        if name in EMPLOYEE_MAP:
            name = EMPLOYEE_MAP[name]
        try:
            int(name)
            emps = Employee.objects.filter(id=name)
        except ValueError:
            if name == 'NN':
                emps = Employee.objects.filter(user__first_name='Nieznany')
            elif len(name) == 3:
                emps = Employee.objects.filter(user__first_name__istartswith=name[0],
                                               user__last_name__istartswith=name[1:3],
                                               status=0)
            else:
                emps = Employee.objects.filter(user__first_name__istartswith=name[0],
                                               user__last_name__istartswith=name[1:],
                                               status=0)
        if len(emps) == 1:
            return emps[0]
        elif len(emps) > 1:
            self.stdout.write(self.style.ERROR(u'Multiple employee matches for {}. Choices are:'
                              .format(name)))
            for e in emps:
                self.stdout.write(self.style.ERROR(u' -{}'.format(e.user.get_full_name())))
        else:
            raise CommandError(u'Employee {} does not exists! Fix your input file.'.format(name))

        return None

    def create_or_update_group(self, course, data, create_terms=True):
        try:
            sync_data_object = TermSyncData.objects.get(scheduler_id=data['id'])
        except TermSyncData.DoesNotExist:
            if create_terms:
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
            self.stdout.write(self.style.SUCCESS(u'Group with scheduler_id={} created!'
                                                 .format(data['id'])))
            self.stdout.write(self.style.SUCCESS(u'  time: {}-{}'
                                                 .format(data['start_time'], data['end_time'])))
            self.stdout.write(self.style.SUCCESS(u'  teacher: {}'
                                                 .format(data['teacher'])))
            self.stdout.write(self.style.SUCCESS(u'  classrooms: {}\n'
                                                 .format(data['classrooms'])))
            self.created_terms += 1
        else:
            term = sync_data_object.term
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
            if set(term.classrooms.all()) != set(data['classrooms']):
                diffs.append(('classroom', (set(term.classrooms.all()), set(data['classrooms']))))
                if create_terms:
                    term.classrooms = data['classrooms']  # this already saves the relation!
            if diffs:
                if create_terms:
                    term.save()
                    term.group.save()
                self.stdout.write(self.style.SUCCESS(u'Group {} {} updated. Difference:'
                                  .format(str(term.group).decode('utf-8'),
                                          str(term).decode('utf-8'))))
                for diff in diffs:
                    self.stdout.write(self.style.WARNING(u'  {}: '.format(diff[0])), ending='')
                    self.stdout.write(self.style.NOTICE(diff[1][0]), ending='')
                    self.stdout.write(self.style.WARNING(u' -> '), ending='')
                    self.stdout.write(self.style.SUCCESS(str(diff[1][1])))
                self.stdout.write(u'\n')
                self.updated_terms += 1

    def prepare_group(self, g, results, terms):
        """Convert information about group from scheduler format."""
        if g['id'] not in results:
            return None
        group = {
            'id': g['id'],
            'entity_name': g['extra']['course'],
            'group_type': GROUP_TYPES[g['extra']['group_type']],
            'teacher': self.get_employee(g['teachers'][0])
        }

        # start_time will be determined as the minimum start_time among all terms
        # end_time - as maximum. All the terms in scheduler are one hour long.
        start_time = 24  # acts as inifinity
        end_time = 0
        classrooms = set()
        for t in results[g['id']]:
            t_start = terms[t['term']]['start']['hour']
            t_end = terms[t['term']]['end']['hour']
            if t_start < start_time:
                start_time = t_start
            if t_end > end_time:
                end_time = t_end
            group['dayOfWeek'] = str(terms[t['term']]['day'] + 1)
            classrooms.add(t['room'])
        group['start_time'] = time(hour=int(start_time))
        group['end_time'] = time(hour=int(end_time))
        group['classrooms'] = self.get_classrooms(list(classrooms))
        group['limit'] = LIMITS[group['group_type']]
        return group

    def get_groups(self):
        client = requests.session()
        client.get(URL_LOGIN)
        csrftoken = client.cookies['csrftoken']
        login_data = {'username': 'test', 'password': 'test', 'csrfmiddlewaretoken': csrftoken,
                      'next': URL_ASSIGNMENTS}
        r = client.post(URL_LOGIN, data=login_data)
        r2 = client.get(URL_SCHEDULE)
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
                self.stdout.write(self.style.WARNING(u'Group number {} does not have a term ({})\n'
                                  .format(g['id'], g['extra']['course'])))
        return groups

    @transaction.atomic
    def import_from_api(self, create_courses=False, create_terms=True):
        self.created_terms = 0
        self.updated_terms = 0
        self.created_courses = 0
        self.used_courses = set()
        groups = self.get_groups()
        for g in groups:
            entity = self.get_entity(g['entity_name'])
            if entity is not None:
                course = self.get_course(entity, create_courses)
                if course is None:
                    raise CommandError(u'Course {} does not exist! Check your input file.'
                                       .format(entity))
                self.create_or_update_group(course, g, create_terms)
        self.stdout.write(self.style.SUCCESS(u'Created {} courses successfully! '
                                             'Moreover {} courses were already there.'
                          .format(self.created_courses, len(self.used_courses))))
        self.stdout.write(self.style.SUCCESS(u'Created {} terms and updated {} terms successfully!'
                          .format(self.created_terms, self.updated_terms)))

    def handle(self, *args, **options):
        self.semester = (Semester.objects.get_next() if options['semester'] == 0
                         else Semester.objects.get(pk=int(options['semester'])))
        self.verbosity = options['verbosity']
        if self.verbosity >= 1:
            self.stdout.write('Adding to semester: {}\n'.format(self.semester))
        if options['dry_run']:
            if self.verbosity >= 1:
                self.stdout.write('Dry run is on. Nothing will be saved.')
            self.import_from_api(False, False)
        else:
            self.import_from_api(options['create_courses'])
