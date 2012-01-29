# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.utils import simplejson

from apps.enrollment.courses.models         import *
from apps.enrollment.records.models          import *

from apps.enrollment.courses.exceptions import NonCourseException
from apps.users.models import BaseUser

import logging
from django.conf import settings
logger = logging.getLogger()


def main(request):
    return render_to_response( 'enrollment/main.html', {}, context_instance = RequestContext( request ))

def prepare_courses_list_to_render(request,default_semester=None,user=None, student=None):
    ''' generates template data for filtering and list of courses '''
    if not default_semester:
        default_semester = Semester.get_default_semester()
    if not user:
        user = request.user
    
   
    semesters = Semester.objects.filter(visible=True)   
    courses = Course.visible.all().order_by('name').values('id', 'name', 'type', 'slug', 'english', 'exam', 'suggested_for_first_year', 'semester')

    semester_courses_list = {}
    semester_courses_list_setdefault = semester_courses_list.setdefault

    # ponieważ: a) to poniższe i tak nam nie działa w systemie (jak teraz doszłam, na dole porównujemy entity_id z course_id, więc ma prawo
    # nie działać (ale mogę się mylić); b) jest tu bardzo wolne zapytanie, które trzeba jakoś zoptymalizować
    """
    if user.is_anonymous():
        records_history = []
    else:
        try:
            if not student:
                student = user.student
            records_history = student.get_records_history(default_semester) # bardzo wolne zapytanie, zajmuje połowę czasu
        except Student.DoesNotExist:
            records_history = []
    """

    for course in courses:
        course['was_enrolled'] = False #course['id'] in records_history -----> poprawić, patrz komentarz powyżej
        semester_courses_list_setdefault(course['semester'],[]).append(course)

    semester_courses = []
    semester_courses_append = semester_courses.append
    for semester in semesters:
        semester_courses_append({
            'id': semester.pk,
            'name': semester.get_name(),
            'is_current': semester.is_current_semester(), #TODO: być może zbędne
            'is_default': (semester == default_semester),
            'courses': semester_courses_list[semester.id]
        })

    render_data = {
        'semester_courses': semester_courses,
        'types_list' : Type.get_all_for_jsfilter(),
        'default_semester': default_semester
    }
    return render_data

def prepare_courses_list_to_render_and_return_course(request,default_semester=None,user=None, student=None, course_slug=None):
    ''' generates template data for filtering and list of courses '''
    if not default_semester:
        default_semester = Semester.get_default_semester()
    if not user:
        user = request.user
    
    def map_course(x):
        return {
                'id': x.id, 
                'name': x.name, 
                'type': x.type_id, 
                'slug': x.slug,
                'english': x.english,
                'exam': x.exam,
                'suggested_for_first_year': x.suggested_for_first_year,
                'semester': x.semester_id,
                'was_enrolled': x.was_enrolled
                }
    
    semesters = Semester.objects.filter(visible=True)   
    courses = Course.visible.all().order_by('name')#.values('id', 'name', 'type', 'slug', 'english', 'exam', 'suggested_for_first_year', 'semester')

    semester_courses_list = {}
    semester_courses_list_setdefault = semester_courses_list.setdefault

    # ponieważ: a) to poniższe i tak nam nie działa w systemie (jak teraz doszłam, na dole porównujemy entity_id z course_id, więc ma prawo
    # nie działać (ale mogę się mylić); b) jest tu bardzo wolne zapytanie, które trzeba jakoś zoptymalizować
    """
    if user.is_anonymous():
        records_history = []
    else:
        try:
            if not student:
                student = user.student
            records_history = student.get_records_history(default_semester) # bardzo wolne zapytanie, zajmuje połowę czasu
        except Student.DoesNotExist:
            records_history = []
    """

    result_course = None
    for course in courses:
        course.was_enrolled = False #course['id'] in records_history -----> poprawić, patrz komentarz powyżej
        semester_courses_list_setdefault(course.semester_id,[]).append(map_course(course))
        if course_slug and course_slug==course.slug:
            result_course = course

    semester_courses = []
    semester_courses_append = semester_courses.append
    for semester in semesters:
        semester_courses_append({
            'id': semester.pk,
            'name': semester.get_name(),
            'is_current': semester.is_current_semester(), #TODO: być może zbędne
            'is_default': (semester == default_semester),
            'courses': semester_courses_list[semester.id]
        })
        if result_course and result_course.semester_id==semester.pk:
            result_course.semester = semester

    render_data = {
        'semester_courses': semester_courses,
        'types_list' : Type.get_all_for_jsfilter(),
        'default_semester': default_semester
    }
    return render_data, result_course

def courses(request):
    return render_to_response('enrollment/courses/courses_list.html',
        prepare_courses_list_to_render(request), context_instance=RequestContext(request))

def votes(request, slug):
    from apps.offer.vote.models import SystemState, SingleVote
    data, course = prepare_courses_list_to_render_and_return_course(request, course_slug=slug)

    data['course'] = course
    data['voters'] = map(lambda x: x.student, SingleVote.objects\
                .filter(Q(course__slug=slug),
                            Q(state__semester_winter=data['default_semester']) |
                            Q(state__semester_summer=data['default_semester']))\
                .select_related('student', 'student__user'))
    data['voters_count'] = len(data['voters'])

    return render_to_response('enrollment/courses/voters.html', data, context_instance=RequestContext(request))

def course(request, slug):
    try:
        default_semester = Semester.get_default_semester()
        user = request.user
        
        # Sprawdzamy, czy mamy studenta
        if user.is_anonymous():
            student = None
            student_id = 0
        else:
            try:
                student = user.student
                student_id = student.id
            except Student.DoesNotExist:
                student = None
                student_id = 0
        
        data, course = prepare_courses_list_to_render_and_return_course(request, default_semester=default_semester, user=user, student=student, course_slug=slug)
        
        #course = list(Course.visible.filter(slug=slug).select_related('semester','entity'))
        if not course:
            raise Course.DoesNotExist
        
        course.teachers_list = course.teachers.all() # potencjalnie problem z n zapytaniami do bazy

        groups = list(Group.objects.filter(course=course).
            extra({
                'enrolled': "SELECT COUNT(*) FROM records_record WHERE courses_group.id=records_record.group_id AND status='%s'" % (STATUS_ENROLLED,),
                'queued': "SELECT COUNT(*) FROM records_queue WHERE courses_group.id=records_queue.group_id",
                'priority': "SELECT COALESCE((SELECT priority FROM records_queue WHERE courses_group.id=records_queue.group_id AND records_queue.student_id=%s),-1)" % (student_id,),
                'signed': "SELECT COALESCE((SELECT id FROM records_record WHERE courses_group.id=records_record.group_id AND status='%s' AND records_record.student_id=%s),0)" % (STATUS_ENROLLED,student_id)}).
            select_related('teacher', 'teacher__user'))
        
        ## TODO: zrobić sortowanie groups w pythonie po terminach

        # Póki co można to usunąć, bo nie ma wymagań w systemie i będzie tu problem n zapytań -> trzeba napisać sql ręcznie
        requirements = []
        #requirements = map(lambda x: x.name, course.requirements.all())
        
        if not student:
                course.is_recording_open = False
                for g in groups:
                    g.is_in_diff = False
                    g.signed = False
                pass
        else:
            enrolled_pinned_queued_ids_sql = """
            SELECT 
                array(SELECT group_id FROM records_record WHERE status=%s AND records_record.student_id=%s) AS enrolled_ids, 
                array(SELECT group_id FROM records_record WHERE status=%s AND records_record.student_id=%s) AS pinned_ids,
                array(SELECT group_id FROM records_queue WHERE records_queue.student_id=%s) AS queued_ids
            """
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute(enrolled_pinned_queued_ids_sql, [STATUS_ENROLLED, student_id, STATUS_PINNED, student_id, student_id])
            (enrolled_ids, pinned_ids, queued_ids) = cursor.fetchall()[0]
            
            queued = Queue.queued.filter(group__course=course).values('priority','group_id')
            queue_priorities = Queue.queue_priorities_map_values(queued)

            course.can_enroll_from = course.get_enrollment_opening_time(student)
            course.is_recording_open = course.can_enroll_from and True or False
            if course.can_enroll_from:
                course.can_enroll_interval = course.can_enroll_from - datetime.now()
            
            for g in groups:
                # TODO to poniżej
                #g.is_in_diff = [group.id for group in student_groups if group.type == g.type]
                g.serialized = simplejson.dumps(g.serialize_for_ajax(
                    enrolled_ids, queued_ids, pinned_ids,
                    queue_priorities, student, user=user
                ))
        
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

        groups_ids = [g.id for g in groups]

        # Tworzymy listę słownik terminów(term_list: group_id -> [terminy jako stringi])   ....jedno zapytanie sql
        terms_list = {}
        terms_list_get = terms_list.get
        terms_list_setdefault = terms_list.setdefault
        terms = Term.get_groups_terms(groups_ids)
        for term in terms:
            terms_list_setdefault(term['group_id'],[]).append(term['term_as_string'])
        
        
        for g in groups:
            g.terms_list = terms_list_get(g.id,[])

            if g.limit_zamawiane > 0 and student and not student.is_zamawiany():
                g.is_full = (g.get_count_of_enrolled_non_zamawiane() >=
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

        # Statystyki wyświetlane tylko adminom (nieadmin -> 0 zapytań sql, admin -> 1 zapytanie sql)
        statistics = {}
        for group_type in xrange(1,11):
            statistics[str(group_type)] = {"in_group": 0, "in_queue": 0}  

        if request.user.is_staff:
            from django.db import connection
            cursor = connection.cursor()
            statistics_sql = """
                SELECT type, SUM(s), COUNT(s) FROM
                (
                    SELECT type, student_id, MAX(rodzaj) as s FROM 
                    ( 
                            SELECT records_record.student_id, courses_group."type", 1 as rodzaj FROM courses_group
                            JOIN records_record ON (records_record.group_id = courses_group.id)
                            WHERE records_record.status = '1' AND courses_group.course_id = %s
                        UNION
                            SELECT DISTINCT records_queue.student_id, courses_group."type", 0 as rodzaj FROM courses_group
                            JOIN records_queue ON (records_queue.group_id = courses_group.id)
                            WHERE courses_group.course_id = %s
                    ) AS r
                    GROUP BY type, student_id
                ) AS p
                GROUP BY type
            """
            cursor.execute(statistics_sql, [course.id, course.id])
            for row in cursor.fetchall():
                try:
                    statistics[str(row[0])] = {"in_group": row[1], "in_queue": row[2]-row[1]}
                except:
                    pass

        tutorials = [
            { 'name' : 'Wykłady', 'groups' : lectures, 'type' : 1, 'statistics':statistics['1']},
            { 'name' : 'Repetytorium', 'groups' : repertory, 'type' : 9, 'statistics':statistics['9']},
            { 'name' : 'Ćwiczenia', 'groups' : exercises, 'type' : 2, 'statistics':statistics['2']},
            { 'name' : 'Pracownia', 'groups' : laboratories, 'type' : 3, 'statistics':statistics['3']},
            { 'name' : 'Ćwiczenia (poziom zaawansowany)', 'groups' : exercises_adv, 'type' : 4, 'statistics':statistics['4']},
            { 'name' : 'Ćwiczenio-pracownie', 'groups' : exer_labs, 'type' : 5, 'statistics':statistics['5']},
            { 'name' : 'Seminarium', 'groups' : seminar, 'type' : 6, 'statistics':statistics['6']},
            { 'name' : 'Lektorat', 'groups' : language, 'type' : 7, 'statistics':statistics['7']},
            { 'name' : 'Zajęcia sportowe', 'groups' : sport, 'type' : 8, 'statistics':statistics['8']},
            { 'name' : 'Projekt', 'groups' : project, 'type' : 10, 'statistics':statistics['10']},
            ]

        courseView_details_hidden = request.COOKIES.get('CourseView-details-hidden', False) == 'true'
        
        data.update({
            'details_hidden': courseView_details_hidden,
            'course' : course,
            'course_json': simplejson.dumps(course.serialize_for_ajax(student, is_recording_open=course.is_recording_open)),
            'points' : course.get_points(student),
            'tutorials' : tutorials,
            'priority_limit': settings.QUEUE_PRIORITY_LIMIT,
            'requirements' : requirements
        })

        return render_to_response( 'enrollment/courses/course.html', data, context_instance = RequestContext( request ) )

    except (Course.DoesNotExist, NonCourseException):
        raise Http404


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
