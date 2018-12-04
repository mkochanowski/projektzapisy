from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.enrollment.courses.models.group import Group
from apps.notifications2.api import notify_user, notify_selected_users
from apps.notifications2.models import get_all_users_in_course_groups


@receiver(post_save, sender=Group)
def notify_that_group_was_added_in_subject(sender: Group, **kwargs) -> None:
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
