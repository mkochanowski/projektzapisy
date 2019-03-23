from django.core.management.base import BaseCommand
from apps.grade.ticket_create.models.student_graded import StudentGraded
from apps.grade.ticket_create.models.signing_key import SigningKey


class Command(BaseCommand):
    args = '<semester( szablon)+>'
    help = 'tworzy ankiety na podstawie szablony'

    def handle(self, *args, **options):
        for signingkey in SigningKey.objects.select_related('students', 'poll', 'poll__semester').all():
            for student in signingkey.students.objects.all():
            st, c = StudentGraded.objects.get_or_create(student=student, semester=signingkey.poll.semester)
