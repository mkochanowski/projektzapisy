from typing import Dict

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.enrollment.courses.models.group import Group
from apps.notifications2.api import notify_user, notify_selected_users
from apps.notifications2.models import get_all_users_in_course_groups
from apps.notifications2.custom_signals import student_pulled


@receiver(post_save, sender=Group)
def notify_that_group_was_added_in_course(sender: Group, **kwargs) -> None:
    group = kwargs["instance"]
    if kwargs["created"] and group.course.information:
        course_groups = Group.objects.filter(course=group.course)
        course_name = group.course.information.entity.name

        teacher = group.teacher.user
        notify_user(teacher, "assigned_to_new_group_as_teacher", {"course_name": course_name})

        users = get_all_users_in_course_groups(course_groups)
        notify_selected_users(users, "added_new_group", {
            "course_name": course_name,
            "teacher": teacher.get_full_name()
        })


@receiver(student_pulled, sender=Group)
def notify_that_user_was_pulled_from_queue(sender: Group, **kwargs) -> None:
    group = kwargs["instance"]
    group_types: Dict = {"1": "wykład", "2": "ćwiczenia", "3": "pracownia", "5": "ćwiczenio-pracownia",
                         "6": "seminarium", "7": "lektorat", "8": "WF", "9": "repetytorium", "10": "projekt"}

    notify_user(kwargs["user"], "pulled_from_queue", {
        "course_name": group.course.information.entity.name,
        "teacher": group.teacher.user.get_full_name(),
        "type": group_types[str(group.type)]
    })
