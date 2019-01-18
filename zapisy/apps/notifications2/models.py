from typing import List
from django.db import models

from apps.enrollment.courses.models.group import Group
from apps.enrollment.records.models import Record, Queue
from django.contrib.auth.models import User


def get_all_users_in_course_groups(course_groups: List[Group]):
    queues = Queue.objects.filter(group__in=course_groups, deleted=False).select_related(
        'student', 'student__user')
    records = Record.objects.filter(group__in=course_groups, status=1).select_related(
        'student', 'student__user')

    return {element.student.user for element in queues} | {element.student.user for element in records}


class NotificationPreferences2(models.Model):
    user = models.ForeignKey(User, verbose_name='użytkownik', on_delete=models.CASCADE)
    add_to_group = models.BooleanField(default=True, verbose_name='Dodano do grupy')
    add_new_group = models.BooleanField(default=True, verbose_name='Dodano nową grupe')
    classroom_change = models.BooleanField(default=True, verbose_name='Zmieniono sale')
