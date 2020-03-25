"""Views for timetable and prototype."""
import csv
import json
from typing import List

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import Http404, HttpResponse, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.enrollment.courses.models import CourseInstance, Group, Semester
from apps.enrollment.courses.templatetags.course_types import \
    decode_class_type_singular
from apps.enrollment.records.models import Record, RecordStatus
from apps.enrollment.timetable.models import Pin
from apps.schedule.models.term import Term as SchTerm
from apps.users.decorators import student_required
from apps.users.models import Employee, Student


def build_group_list(groups: List[Group]):
    """Builds a serializable object containing relevant information about groups

    The information must be sufficient to display information in the timetable
    and perform actions (enqueuing/dequeuing).
    """
    stats = Record.groups_stats(groups)
    group_dicts = []
    group: Group
    for group in groups:
        group_dict = model_to_dict(group, fields=['id', 'limit', 'extra'])
        term_dicts = []
        for term in group.term.all():
            term_dict = model_to_dict(term, fields=['dayOfWeek', 'start_time', 'end_time'])
            term_dict['classrooms'] = term.numbers()
            term_dicts.append(term_dict)
        guaranteed_spots = [{
            'role': gs.role.name,
            'limit': gs.limit,
        } for gs in group.guaranteed_spots.all()]
        group_dict.update({
            'course': {
                'url': reverse('course-page', args=(group.course.slug, )),
                'name': group.course.name,
                'shortName': group.course.short_name,
            },
            'type': decode_class_type_singular(group.type),
            'url': reverse('group-view', args=(group.pk, )),
            'teacher': {
                'id': group.teacher_id,
                'url': reverse('employee-profile', args=(group.teacher.user_id, )),
                'name': group.teacher.user.get_full_name(),
            },
            'num_enrolled': stats.get(group.pk).get('num_enrolled'),
            'term': term_dicts,
            'guaranteed_spots': guaranteed_spots,
            'is_enrolled': getattr(group, 'is_enrolled', None),
            'is_enqueued': getattr(group, 'is_enqueued', None),
            'is_pinned': getattr(group, 'is_pinned', None),
            'can_enqueue': getattr(group, 'can_enqueue', None),
            'can_dequeue': getattr(group, 'can_dequeue', None),
            'action_url': reverse('prototype-action', args=(group.pk, )),
        })
        group_dicts.append(group_dict)
    return group_dicts


def list_courses_in_semester(semester: Semester):
    """Returns a JSON of all the course names in semester.

    This list will be used in prototype.
    """
    qs = CourseInstance.objects.filter(semester=semester).prefetch_related('effects', 'tags')
    courses = []
    for course in qs:
        course_dict = course.__json__()
        course_dict.update({
            'url': reverse('prototype-get-course', args=(course.id,)),
        })
        courses.append(course_dict)
    return json.dumps(list(courses))


def student_timetable_data(student: Student):
    """Collects the timetable data for a student."""
    semester = Semester.objects.get_next()
    # This costs an additional join, but works if there is no current semester.
    records = Record.objects.filter(
        student=student,
        group__course__semester=semester, status=RecordStatus.ENROLLED).select_related(
            'group__teacher', 'group__teacher__user', 'group__course').prefetch_related(
                'group__term', 'group__term__classrooms', 'group__guaranteed_spots',
                'group__guaranteed_spots__role')
    groups = [r.group for r in records]
    group_dicts = build_group_list(groups)

    points_for_courses = {r.group.course.id: r.group.course.points for r in records}

    data = {
        'groups': groups,
        'sum_points': sum(points_for_courses.values()),
        'groups_json': json.dumps(group_dicts, cls=DjangoJSONEncoder),
    }
    return data


def employee_timetable_data(employee: Employee):
    """Collects the timetable data for an employee."""
    semester = Semester.objects.get_next()
    groups = Group.objects.filter(teacher=employee, course__semester=semester).select_related(
        'teacher', 'teacher__user', 'course').prefetch_related(
            'term', 'term__classrooms', 'guaranteed_spots', 'guaranteed_spots__role')
    group_dicts = build_group_list(groups)
    data = {
        'groups_json': json.dumps(group_dicts, cls=DjangoJSONEncoder),
    }
    return data


@login_required
def my_timetable(request):
    """Shows the student/employee his own timetable page."""
    if request.user.student:
        data = student_timetable_data(request.user.student)
    elif request.user.employee:
        data = employee_timetable_data(request.user.employee)
    else:
        messages.error(
            request,
            "Nie masz planu zajęć, ponieważ nie jesteś ani studentem ani pracownikiem.")
        return redirect("course-list")

    return render(request, 'timetable/timetable.html', data)


@student_required
def my_prototype(request):
    """Renders the prototype with enrolled, enqueued, and pinned groups."""
    student = request.user.student
    semester = Semester.objects.get_next()

    # This costs an additional join, but works if there is no current semester.
    records = Record.objects.filter(
        student=student,
        group__course__semester=semester).exclude(status=RecordStatus.REMOVED).select_related(
            'group__teacher', 'group__teacher__user',
            'group__course', 'group__course__semester').prefetch_related(
                'group__term', 'group__term__classrooms', 'group__guaranteed_spots',
                'group__guaranteed_spots__role')
    pinned = Pin.student_pins_in_semester(student, semester)
    pinned = list(pinned)
    all_groups_by_id = {r.group_id: r.group for r in records}
    all_groups_by_id.update({p.pk: p for p in pinned})
    all_groups = list(all_groups_by_id.values())
    can_enqueue_dict = Record.can_enqueue_groups(student, all_groups)
    can_dequeue_dict = Record.can_dequeue_groups(student, all_groups)

    for record in records:
        group = all_groups_by_id.get(record.group_id)
        group.is_enrolled = record.status == RecordStatus.ENROLLED
        group.is_enqueued = record.status == RecordStatus.QUEUED

    for pin in pinned:
        group = all_groups_by_id.get(pin.pk)
        group.is_pinned = True

    all_groups = all_groups_by_id.values()
    for group in all_groups:
        group.can_enqueue = can_enqueue_dict.get(group.pk)
        group.can_dequeue = can_dequeue_dict.get(group.pk)

    group_dicts = build_group_list(all_groups)
    filters_dict = CourseInstance.prepare_filter_data(
        CourseInstance.objects.filter(semester=semester))
    courses_json = list_courses_in_semester(semester)
    data = {
        'groups_json': json.dumps(group_dicts, cls=DjangoJSONEncoder),
        'filters_json': json.dumps(filters_dict, cls=DjangoJSONEncoder),
        'courses_json': courses_json,
    }
    return render(request, 'timetable/prototype.html', data)


@student_required
@require_POST
def prototype_action(request, group_id):
    """Performs actions requested by timetable prototype.

    HTTP response 204 (successful with no content to send back) will be returned
    if the pin operation is performed with no obstacles. If the student is not
    allowed to perform an operation, 403 (forbidden) status shall be returned.
    """
    student = request.user.student
    group: Group
    try:
        group = Group.objects.get(pk=group_id)
    except Group.DoesNotExist:
        raise Http404
    # Axios sends POST data in json rather than _Form-Encoded_.
    data = json.loads(request.body.decode('utf-8'))
    action = data.get('action')
    if action == 'pin':
        Pin.objects.get_or_create(student_id=student.pk, group_id=group_id)
        return HttpResponse(status=204)
    if action == 'unpin':
        Pin.objects.filter(student_id=student.pk, group_id=group_id).delete()
        return HttpResponse(status=204)
    if action == 'enqueue':
        group_ids = Record.enqueue_student(student, group)
        if group_ids:
            # When the student joins the queue of a class, the accompanying
            # lecture group might need to be displayed (if he is automatically
            # enqueued in that). We hence send him the information about these
            # groups.
            groups = Group.objects.filter(pk__in=group_ids).select_related(
                'teacher', 'teacher__user', 'course', 'course__semester').prefetch_related(
                    'term', 'term__classrooms', 'guaranteed_spots', 'guaranteed_spots__role')
            for group in groups:
                group.is_enqueued = True
            groups_dicts = build_group_list(groups)
            return JsonResponse(groups_dicts, safe=False)
        else:
            return HttpResponse(status=403)
    if action == 'dequeue':
        group_ids = Record.remove_from_group(student, group)
        if group_ids:
            return JsonResponse(group_ids, safe=False)
        else:
            return HttpResponse(status=403)
    # If the request action is not among the above, we return Bad Request
    # response.
    return HttpResponse(status=400, content=action)


@student_required
def prototype_get_course(request, course_id):
    """Retrieves the annotated groups of a single course."""
    student = request.user.student
    course = CourseInstance.objects.get(pk=course_id)
    groups = course.groups.exclude(extra='hidden').select_related(
        'course', 'teacher', 'course__semester', 'teacher__user'
    ).prefetch_related('term', 'term__classrooms', 'guaranteed_spots', 'guaranteed_spots__role')
    can_enqueue_dict = Record.can_enqueue_groups(student, groups)
    can_dequeue_dict = Record.can_dequeue_groups(student, groups)
    for group in groups:
        group.can_enqueue = can_enqueue_dict.get(group.pk)
        group.can_dequeue = can_dequeue_dict.get(group.pk)
    group_dicts = build_group_list(groups)
    return JsonResponse(group_dicts, safe=False)


@student_required
@require_POST
def prototype_update_groups(request):
    """Retrieves the updated group annotations.

    The list of groups ids to update will be sent in JSON body of the request.
    """
    student = request.user.student
    semester = Semester.objects.get_next()
    # Axios sends POST data in json rather than _Form-Encoded_.
    ids: List[int] = json.loads(request.body.decode('utf-8'))
    num_enrolled = Count('record', filter=Q(record__status=RecordStatus.ENROLLED))
    is_enrolled = Count(
        'record',
        filter=(Q(record__status=RecordStatus.ENROLLED, record__student_id=student.pk)))
    is_enqueued = Count(
        'record',
        filter=(Q(record__status=RecordStatus.QUEUED, record__student_id=student.pk)))

    groups_from_ids = Group.objects.filter(pk__in=ids)
    groups_enrolled_or_enqueued = Group.objects.filter(
        course__semester=semester,
        record__status__in=[RecordStatus.QUEUED, RecordStatus.ENROLLED],
        record__student=student)
    groups_all = groups_from_ids | groups_enrolled_or_enqueued
    groups = groups_all.annotate(num_enrolled=num_enrolled).annotate(
        is_enrolled=is_enrolled).annotate(is_enqueued=is_enqueued).select_related(
            'course', 'teacher', 'course__semester', 'teacher__user').prefetch_related(
                'term', 'term__classrooms', 'guaranteed_spots', 'guaranteed_spots__role')

    can_enqueue_dict = Record.can_enqueue_groups(student, groups)
    can_dequeue_dict = Record.can_dequeue_groups(student, groups)
    for group in groups:
        group.can_enqueue = can_enqueue_dict.get(group.pk)
        group.can_dequeue = can_dequeue_dict.get(group.pk)
        group.is_enqueued = bool(group.is_enqueued)
        group.is_enrolled = bool(group.is_enrolled)
    group_dicts = build_group_list(groups)
    return JsonResponse(group_dicts, safe=False)


@login_required
def calendar_export(request):
    """Exports user's timetable for import in Google Calendar."""
    semester = Semester.objects.get_next()
    groups = Group.objects.filter(course__semester=semester).filter(
        Q(teacher__user=request.user) | Q(record__student__user=request.user))
    terms = SchTerm.objects.filter(event__group__in=groups).select_related(
        'event__group', 'event__group__course', 'event__group__teacher',
        'event__group__teacher__user', 'room')

    response = HttpResponse(content_type='text/csv')
    response['Content-disposition'] = 'attachment; filename="calendar.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Location', 'Description'])
    for term in terms:
        group = term.event.group
        room = term.room

        name = f"{group.course.name} - {group.get_type_display()}"
        location = f"Sala {room.number}, Instytut Informatyki Uniwersytetu Wrocławskiego"
        description = f"Prowadzący: {group.get_teacher_full_name()}"
        writer.writerow([name, term.day, term.start, term.day, term.end, location, description])
    return response
