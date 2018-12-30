import uuid

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models


class GradingSession(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tickets = JSONField()

    class Meta:
        verbose_name = 'sesja oceniania zajęć'
        verbose_name_plural = 'sesje oceniania zajęć'
        app_label = 'poll'
