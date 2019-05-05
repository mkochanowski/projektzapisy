"""This code exists only to enable signals."""
from django.apps import AppConfig


class PollLegacyAppConfig(AppConfig):
    name = "apps.grade.poll"
    verbose_name = "Poll - legacy"

class PollAppConfig(AppConfig):
    name = "apps.grade.poll"
    verbose_name = "Poll - refactored"

    def ready(self):
        import apps.grade.poll.signals