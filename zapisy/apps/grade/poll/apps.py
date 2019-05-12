from django.apps import AppConfig


class PollAppConfig(AppConfig):
    name = "apps.grade.poll"
    verbose_name = "Poll - refactored"

    def ready(self):
        import apps.grade.poll.signals
