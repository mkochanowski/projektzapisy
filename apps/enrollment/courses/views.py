# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts               import render_to_response
from django.template                import RequestContext

from apps.enrollment.courses.models         import *
from apps.enrollment.records.models          import *

from apps.enrollment.courses.exceptions import NonCourseException
from apps.users.models import BaseUser

import logging
from django.conf import settings
logger = logging.getLogger()


def main(request):
    return render_to_response( 'enrollment/main.html', {}, context_instance = RequestContext( request ))

def prepare_courses_list_to_render(request):
    ''' generates template data for filtering and list of courses '''
    
    semesters = Semester.objects.filter(visible=True)
    courses = Course.visible.all()

    if request.user.is_anonymous():
        records_history = []
    else:
        try:
            student = request.user.student
            records_history = student.get_records_history()
        except Student.DoesNotExist:
            records_history = []

    default_semester = Semester.get_default_semester()

    semester_courses = []
    for semester in semesters:
        semester_courses.append({
            'id': semester.pk,
            'name': semester.get_name(),
            'is_current': semester.is_current_semester(), #TODO: być może zbędne
            'is_default': (semester == default_semester),
            'courses': courses.filter(semester__id__exact=semester.pk).
                order_by('name').values('id', 'name', 'type', 'slug')
        })
    for semester in semester_courses:
        for course in semester['courses']:
            course.update({ 'was_enrolled' : course['id'] in records_history })

    render_data = {
        'semester_courses': semester_courses,
        'types_list' : Type.get_all_for_jsfilter(),
        'default_semester': Semester.get_default_semester()
    }
    return render_data


def courses(request):
    return render_to_response('enrollment/courses/courses_list.html',
        prepare_courses_list_to_render(request), context_instance=RequestContext(request))

   
def course(request, slug):
    try:
        course = Course.visible.get(slug=slug)

        enrolled = Record.enrolled.filter(group__course=course)
        pinned = Record.pinned.filter(group__course=course)
        queued = Queue.queued.filter(group__course=course)

        groups = list(Group.objects.filter(course=course).
            order_by('term__dayOfWeek','term__start_time','term__end_time'))
        seen = []
        seen_append = seen.append
        groups = [ x for x in groups if x not in seen and not seen_append(x)]

        requirements = map(lambda x: x.name, course.requirements.all())
        if request.user.is_anonymous():
                student = None
                course.is_recording_open = False
                student_queues = None
                student_groups = None
                for g in groups:
                    g.priority = None
                    g.is_in_diff = False
                    g.signed = False
                pass
        else:
            try:
                student = request.user.student

                enrolled_ids = enrolled.filter(student=student).values_list('group__id', flat=True)
                queued_ids = queued.filter(student=student).values_list('group__id', flat=True)
                pinned_ids = pinned.filter(student=student).values_list('group__id', flat=True)
                queue_priorities = Queue.queue_priorities_map(queued)

                course.is_recording_open = course.is_recording_open_for_student(student)
                course.can_enroll_from = course.get_enrollment_opening_time(student)
                if course.can_enroll_from:
                    course.can_enroll_interval = course.can_enroll_from - datetime.now()
                
                student_queues = queued.filter(student=student)
                student_queues_groups = map(lambda x: x.group, student_queues)
                student_groups = map(lambda x: x.group, enrolled.filter(student=student))

                student_counts = Group.get_students_counts(groups)

                for g in groups:
                    if g in student_queues_groups:
                        g.priority = student_queues.get(group=g).priority
                    g.is_in_diff = [group.id for group in student_groups if group.type == g.type]
                    if g in student_groups:
                        g.signed = True
                    g.serialized = g.serialize_for_ajax(
                        enrolled_ids, queued_ids, pinned_ids,
                        queue_priorities, student_counts, student
                    )
            except Student.DoesNotExist:
                student = None
                course.is_recording_open = False
                student_queues = None
                student_groups = None
                for g in groups:
                    g.priority = None
                    g.is_in_diff = False
                    g.signed = False
                pass

        
        lectures = []
        exercises = []
        laboratories = []
        exercises_adv = []
        exer_labs = []
        seminar = []
        language = []
        sport = []
        repertory = []
        project = []


        for g in groups:
            g.enrolled = enrolled.filter(group=g).count()
            g.queued = queued.filter(group=g).count()

            if g.limit_zamawiane > 0 and student and not student.is_zamawiany():
                g.is_full = (g.number_of_students_non_zamawiane() >=
                    g.limit_non_zamawiane())
            else:
                g.is_full = (g.enrolled >= g.limit)

            if g.type == '1': #faster in good case, bad case - same
                lectures.append(g);
            elif g.type == '2':
                exercises.append(g);
            elif g.type == '3':
                laboratories.append(g);
            elif g.type == '4':
                exercises_adv.append(g);
            elif g.type == '5':
                exer_labs.append(g);
            elif g.type == '6':
                seminar.append(g);
            elif g.type == '7':
                language.append(g);
            elif g.type == '8':
                sport.append(g);
            elif g.type == '9':
                repertory.append(g);
            elif g.type == '10':
                project.append(g);
            else:
                break

        '''lectures = groups.filter(type='1') #probably better, but you can't extend objects in QuerySet
        exercises = groups.filter(type='2')
        laboratories = groups.filter(type='3')
        exercises_adv = groups.filter(type='4')
        exer_labs = groups.filter(type='5')
        seminar = groups.filter(type='6')
        language = groups.filter(type='7')
        sport = groups.filter(type='8')

        lectures.name = "Wykłady"
        exercises.name = "Ćwiczenia"
        laboratories.name = "Pracownia"
        exercises_adv.name = "Ćwiczenia (poziom zaawansowany)"
        exer_labs.name = "Ćwiczenio-pracownie"
        seminar.name = "Seminarium"
        language.name = "Lektorat"
        sport.name = "Zajęcia"'''

        tutorials = [
            { 'name' : 'Wykłady', 'groups' : lectures, 'type' : 1},
            { 'name' : 'Repetytorium', 'groups' : repertory, 'type' : 9},
            { 'name' : 'Ćwiczenia', 'groups' : exercises, 'type' : 2},
            { 'name' : 'Pracownia', 'groups' : laboratories, 'type' : 3},
            { 'name' : 'Ćwiczenia (poziom zaawansowany)', 'groups' : exercises_adv, 'type' : 4},
            { 'name' : 'Ćwiczenio-pracownie', 'groups' : exer_labs, 'type' : 5},
            { 'name' : 'Seminarium', 'groups' : seminar, 'type' : 6},
            { 'name' : 'Lektorat', 'groups' : language, 'type' : 7},
            { 'name' : 'Zajęcia sportowe', 'groups' : sport, 'type' : 8},
            { 'name' : 'Projekt', 'groups' : project, 'type' : 10},
            ]

        data = prepare_courses_list_to_render(request)
        data.update({
            'course' : course,
            'points' : course.get_points(student),
            'tutorials' : tutorials,
            'priority_limit': settings.QUEUE_PRIORITY_LIMIT,
            'requirements' : requirements
        })

        return render_to_response( 'enrollment/courses/course.html', data, context_instance = RequestContext( request ) )

    except (Course.DoesNotExist, NonCourseException):
        logger.error('Function course(slug = %s) throws Course.DoesNotExist exception.' % unicode(slug) )
        if not request.user.is_anonymous():
            request.user.message_set.create(message="Przedmiot nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))


def course_consultations(request, slug):
    try:
        course = Course.visible.get(slug=slug)
        employees = set(map(lambda x: x.teacher, Group.objects.filter(course=course)))
        data = prepare_courses_list_to_render(request)
        data.update({
            'course' : course,
            'employees' : employees
        })
        return render_to_response( 'enrollment/courses/course_consultations.html', data, context_instance = RequestContext( request ) )

    except (Course.DoesNotExist, NonCourseException):
        logger.error('Function course_consultations(slug = %s) throws Course.DoesNotExist exception.' % unicode(slug) )
        request.user.message_set.create(message="Przedmiot nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))