from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Poll

from apps.enrollment.courses.models.course import Course
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester


@receiver(post_save, sender=Group)
def create_poll_for_group(sender: Group, instance: Group, created: bool, **kwargs):
    if created:
        new_poll = Poll(group=instance, course=None, semester=None)
        new_poll.save()


@receiver(post_save, sender=Course)
def create_poll_for_course(sender: Course, instance: Course, created: bool, **kwargs):
    if created:
        new_poll = Poll(group=None, course=instance, semester=None)
        new_poll.save()


@receiver(post_save, sender=Semester)
def create_poll_for_semester(
    sender: Semester, instance: Semester, created: bool, **kwargs
):
    if created:
        new_poll = Poll(group=None, course=None, semester=instance)
        new_poll.save()
