from typing import Dict

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.enrollment.courses.models.group import Group
from apps.notifications2.api import notify_user, notify_selected_users
from apps.notifications2.models import get_all_users_in_course_groups
from apps.notifications2.custom_signals import student_pulled, teacher_changed


@receiver(post_save, sender=Group)
def notify_that_group_was_added_in_course(sender: Group, **kwargs) -> None:
    group = kwargs['instance']
    if kwargs['created'] and group.course.information:
        course_groups = Group.objects.filter(course=group.course)
        course_name = group.course.information.entity.name

        teacher = group.teacher.user
        notify_user(teacher, 'assigned_to_new_group_as_teacher', {'course_name': course_name})

        users = get_all_users_in_course_groups(course_groups)
        notify_selected_users(users, 'added_new_group', {
            'course_name': course_name,
            'teacher': teacher.get_full_name()
        })


@receiver(student_pulled, sender=Group)
def notify_that_user_was_pulled_from_queue(sender: Group, **kwargs) -> None:
    group = kwargs['instance']

    notify_user(kwargs['user'], 'pulled_from_queue', {
        'course_name': group.course.information.entity.name,
        'teacher': group.teacher.user.get_full_name(),
        'type': group.human_readable_type().lower()
    })


@receiver(teacher_changed, sender=Group)
def notify_that_teacher_was_changed(sender: Group, **kwargs) -> None:
    group = kwargs['instance']

    teacher = group.teacher.user
    course_name = group.course.information.entity.name

    notify_user(teacher, 'assigned_to_new_group_as_teacher', {'course_name': course_name})

    users = get_all_users_in_course_groups([group])
    notify_selected_users(users, 'teacher_has_been_changed', {
        'course_name': course_name,
        'teacher': teacher.get_full_name(),
        'type': group.human_readable_type().lower()
    })
