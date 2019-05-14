from django.contrib.auth import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.enrollment.courses.models.course import Course
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester

from .models import Poll


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


@receiver(user_logged_in)
def clear_saved_submissions(sender, request, **kwargs):
    """Removes submissions from the active session when user performs
        a login."""
    if "grade_poll_submissions" in request.session:
        del request.session["grade_poll_submissions"]
