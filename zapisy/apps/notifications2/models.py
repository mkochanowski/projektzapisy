from typing import List

from apps.enrollment.courses.models.group import Group
from apps.enrollment.records.models import Record, Queue


def get_all_users_in_course_groups(course_groups: List[Group]):
    queues = Queue.objects.filter(group__in=course_groups, deleted=False).select_related(
        'student', 'student__user')
    records = Record.objects.filter(group__in=course_groups, status=1).select_related(
        'student', 'student__user')

    return {element.student.user for element in queues} | {element.student.user for element in records}
