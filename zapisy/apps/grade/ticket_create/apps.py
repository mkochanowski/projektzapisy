from django.apps import AppConfig


class TicketCreateConfig(AppConfig):
    name = 'apps.grade.ticket_create'

    def ready(self):
        import apps.grade.ticket_create.signals