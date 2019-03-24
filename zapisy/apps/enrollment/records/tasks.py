"""The task defined in this module will be run asynchronously by a worker pool.

They will perform actions that must be taken but should not block server
threads. A typical example is, when a student decides to leave a group, we
should not make him wait for another student being pulled from the queue to take
place he leaves vacant.
"""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq import job

from apps.enrollment.courses.models import Group
from apps.enrollment.records.models.opening_times import GroupOpeningTimes
from apps.enrollment.records.models.records import Record
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL


@job
def pull_from_queue(group_id: int):
    """This function will pull students from the queue as long as possible."""
    Record.fill_group(group_id)


@receiver(GROUP_CHANGE_SIGNAL)
def pull_from_queue_signal_receiver(sender, **kwargs):
    """Receives the signal call and runs pull_from_queue.

    Depending on RQ_QUEUES setting it will either run eagerly or asynchronously.
    """
    group_id = kwargs.get('group_id')
    if not settings.RUN_ASYNC:
        pull_from_queue(group_id)
    else:
        pull_from_queue.delay(group_id)


@receiver(post_save, sender=Group)
def group_save_signal_receiver(sender, instance, created, raw, using, **kwargs):
    """Receives the signal when the group is modified.

    The modification might be a limit change or a creation. pull_from_queue
    needs to be run. Depending on RQ_QUEUES setting it will either run eagerly
    or asynchronously.

    For a newly created group will generate opening times, if the opening times
    have been already generated in the semester.
    """
    group_id = instance.pk
    if created:
        # If course has no semester, there is no point generating anything.
        if instance.course.semester is None:
            return
        # Check if opening times have been generated in the semester.
        if not GroupOpeningTimes.objects.filter(
                group__course__semester=instance.course.semester).exists():
            # If not, we do nothing.
            return
        GroupOpeningTimes.populate_single_group_opening_times(instance)
        # Do not trigger pulling for new groups.
        return
    if not settings.RUN_ASYNC:
        pull_from_queue(group_id)
    else:
        pull_from_queue.delay(group_id)
