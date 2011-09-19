# -*- coding: utf-8 -*-

from django.utils import simplejson

from debug_toolbar.panels.timer import TimerDebugPanel

from apps.enrollment.courses.models import Term
from apps.enrollment.records.models import *
from apps.users.models import *

def prepare_courses_with_terms(terms, records = None):
    if records is None:
        records = []
    courses_list = []
    courses_map = {}
    def add_course_to_map(course):
        if course.pk in courses_map:
            return
        course_info = {
            'object': course,
            'info': {
                'id' : course.pk,
                'name': course.name,
                'short': course.entity.get_short_name(),
                'type': course.type and course.type.pk or 1,
                'slug': course.slug,
		'exam': course.exam,
		'english': course.english,
		'suggested_for_first_year': course.suggested_for_first_year,
            },
            'terms': []
        }
        courses_map[course.pk] = course_info
        courses_list.append(course_info)
    for term in terms:
        course = term.group.course
        add_course_to_map(course)
        term_info = {
            'id': term.pk,
            'group': term.group.pk,
            'classroom': term.classroom.number or 0,
            'day': int(term.dayOfWeek),
            'start_time': [term.start_time.hour, term.start_time.minute],
            'end_time': [term.end_time.hour, term.end_time.minute],

            #TODO: to chyba zbędne?
            #'enrolled_count': term.group.get_count_of_enrolled(),
            #'queued_count': term.group.get_count_of_queued(),
        }
        courses_map[course.pk]['terms'].append({
            'id': term.pk,
            'object': term,
            'info': term_info
        })
    for record in records:
        add_course_to_map(record.group.course)

    courses_list = sorted(courses_list, \
        key=lambda course: course['info']['name'])
    return courses_list

def prepare_groups_json(semester, groups, student=None, employee=None):
    TimerDebugPanel.timer_start('pgj_1', 'prepare_groups_json - record_ids')
    record_ids = Record.get_student_records_ids(student, semester)
    TimerDebugPanel.timer_stop('pgj_1')
    TimerDebugPanel.timer_start('pgj_2',
        'prepare_groups_json - queue_priorities')
    queue_priorities = Queue.queue_priorities_map(
        Queue.get_student_queues(student, semester))
    TimerDebugPanel.timer_stop('pgj_2')
    groups_json = []
    TimerDebugPanel.timer_start('pgj_3', 'prepare_groups_json - serialize')
    for group in groups:
        groups_json.append(group.serialize_for_ajax(
            record_ids['enrolled'], record_ids['queued'], record_ids['pinned'],
            queue_priorities, student=student, employee=employee
        ))
    TimerDebugPanel.timer_stop('pgj_3')
    return simplejson.dumps(groups_json)

def prepare_courses_json(groups, student):
    courses_json = []
    for group in groups:
        courses_json.append(group.course.serialize_for_ajax(student))
    return simplejson.dumps(courses_json)

def prepare_schedule_courses(request, for_student = None, for_employee = None):
    if not (for_student is None) and not (for_employee is None):
        raise RuntimeError('Nie można wygenerować jednocześnie dla studenta' + \
            ' i pracownika')

    default_semester = Semester.get_default_semester()

    if not for_employee is None:
        terms = Term.get_all_in_semester(default_semester, employee=for_employee)
    else:
        terms = Term.get_all_in_semester(default_semester, student=for_student)

    try:
        student = request.user.student
        records = Record.get_student_enrolled_objects(student, default_semester)
    except Student.DoesNotExist:
        records = []

    return prepare_courses_with_terms(terms, records)

def prepare_schedule_data(request, courses):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        student = None
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        employee = None
    default_semester = Semester.get_default_semester()

    terms_by_days = [None for i in range(8)] # dni numerowane od 1
    for course in courses:
        for term in course['terms']:
            day = int(term['object'].dayOfWeek)
            if not terms_by_days[day]:
                terms_by_days[day] = {
                    'day_id': day,
                    'day_name': term['object'].get_dayOfWeek_display(),
                    'terms': []
                }
            terms_by_days[day]['terms'].append(term)
            term.update({ # TODO: do szablonu
                'json': simplejson.dumps(term['info'])
            })
    terms_by_days = filter(lambda term: term, terms_by_days)

    # TODO: tylko grupy, na które jest zapisany
    all_groups = Group.get_groups_by_semester(default_semester)
    all_groups_json = prepare_groups_json(default_semester, all_groups, \
        student=student, employee=employee)

    from settings import QUEUE_PRIORITY_LIMIT

    return {
        'courses_json': prepare_courses_json(all_groups, student),
        'groups_json': all_groups_json,
        'terms_by_days': terms_by_days,
        'priority_limit': QUEUE_PRIORITY_LIMIT,
    }
