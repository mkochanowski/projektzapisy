# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts               import render_to_response
from django.template                import RequestContext

from apps.enrollment.subjects.models         import *
from apps.enrollment.records.models          import *

from apps.enrollment.subjects.exceptions import NonSubjectException

import logging
logger = logging.getLogger()

''' generates template data for filtering and list of subjects '''
def prepare_subjects_list_to_render(request):
    semesters = Semester.objects.filter(visible=True)
    subjects = Subject.visible.all()

    try:
        student = request.user.student
        records_history = student.get_records_history()
    except Student.DoesNotExist:
        records_history = []

    semester_subjects = []
    for semester in semesters:
        semester_subjects.append({
            'id': semester.pk,
            'name': semester.get_name(),
            'is_current': semester.is_current_semester(),
            'subjects': subjects.filter(semester__id__exact=semester.pk).
                order_by('name').values('id', 'name', 'type', 'slug')
        })
    for semester in semester_subjects:
        for subject in semester['subjects']:
            subject.update( { 'was_enrolled' : subject['id'] in records_history } )

    render_data = {
        'semester_subjects': semester_subjects,
        'types_list' : Type.get_all_for_jsfilter(),
        'default_semester': Semester.get_default_semester()
    }
    return render_data


@login_required
def subjects(request):
    return render_to_response('enrollment/subjects/subjects_list.html',
        prepare_subjects_list_to_render(request), context_instance=RequestContext(request))

   
@login_required
def subject(request, slug):
    try:
        subject = Subject.visible.get(slug=slug)
        records = Record.enrolled.filter(group__subject=subject)
        queues = Queue.queued.filter(group__subject=subject)
        groups = list(Group.objects.filter(subject=subject))
        try:
            student = request.user.student
            subject.is_recording_open = subject.is_recording_open_for_student(student)
            subject.can_enroll_from = subject.get_enrollment_opening_time(student)
            if subject.can_enroll_from:
                subject.can_enroll_interval = subject.can_enroll_from - datetime.now()
            
            student_queues = queues.filter(student=student)
            student_queues_groups = map(lambda x: x.group, student_queues)
            student_groups = map(lambda x: x.group, records.filter(student=student))

            for g in groups:
                if g in student_queues_groups:
                    g.priority = student_queues.get(group=g).priority
                g.enrolled = records
                g.is_in_diff = [group.id for group in student_groups if group.type == g.type]
                if g in student_groups:
                    g.signed = True


            '''records = Record.objects.filter(student=student)    <--- prawdopodobnie niepotrzebne...
            if records:
                for record in records:
                    if ( record.group.subject == subject ):
                        if record.group.type == '2':
                            subject.user_enrolled_to_exercise = True;
                            break;
                        elif record.group.type == '3':
                            subject.user_enrolled_to_laboratory = True;
                            break;
                        elif record.group.type == '4':
                            subject.user_enrolled_to_eaoratory = True;
                            break;
                        elif record.group.type == '5':
                            subject.user_enrolled_to_exlaboratory = True;
                            break;
                        elif record.group.type == '6':
                            subject.user_enrolled_to_seminar = True;
                            break;
                        elif record.group.type == '7':
                            subject.user_enrolled_to_langoratory = True;
                            break;
                        elif record.group.type == '8':
                            subject.user_enrolled_to_ssoratory = True;
                            break;
                        else:
                            break;'''
        except Student.DoesNotExist:
            student = None
            subject.is_recording_open = False
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
            g.enrolled = records.filter(group=g).count()
            g.queued = queues.filter(group=g).count()

            if (g.enrolled >= g.limit):
                g.is_full = True
            else:
                g.is_full = False

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
                break;

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
            { 'name' : 'Wykłady', 'groups' : lectures},
            { 'name' : 'Repetytorium', 'groups' : repertory},
            { 'name' : 'Ćwiczenia', 'groups' : exercises},
            { 'name' : 'Pracownia', 'groups' : exercises_adv},
            { 'name' : 'Ćwiczenia (poziom zaaansowany)', 'groups' : laboratories},
            { 'name' : 'Ćwiczenio-pracownie', 'groups' : seminar},
            { 'name' : 'Seminarium', 'groups' : exer_labs},
            { 'name' : 'Lektorat', 'groups' : language},
            { 'name' : 'Zajęcia', 'groups' : sport},
            { 'name' : 'Project', 'groups' : project},
            ]
        

        data = prepare_subjects_list_to_render(request)
        data.update({
            'subject' : subject,
            'tutorials' : tutorials,
        })

        return render_to_response( 'enrollment/subjects/subject.html', data, context_instance = RequestContext( request ) )

    except (Subject.DoesNotExist, NonSubjectException):
        logger.error('Function subject(slug = %s) throws Subject.DoesNotExist exception.' % unicode(slug) )
        request.user.message_set.create(message="Przedmiot nie istnieje.")
        return render_to_response('common/error.html', context_instance=RequestContext(request))
