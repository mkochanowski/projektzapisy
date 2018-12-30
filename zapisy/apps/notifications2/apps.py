from django.apps import AppConfig


class Notifications2Config(AppConfig):
    name = "apps.notifications2"

    def ready(self):
        import apps.notifications2.signals
