from django.core.management.base import BaseCommand, CommandError
from apps.grade.ticket_create.models import StudentGraded
from django.core.exceptions import ObjectDoesNotExist
from apps.users.models import Student

class Command(BaseCommand):
    args = '<plik semester>'
    help = 'ocenia'

    def handle(self, *args, **options):
        f = open(args[0], 'r')
        for line in f:
            u = StudentGraded()
            try:
                u.student = Student.objects.get(matricula=line)
            except ObjectDoesNotExist:
                pass
            u.semester_id = args[1]
            u.save()