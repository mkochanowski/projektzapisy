from django.core.management.base import BaseCommand, CommandError
from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models.origin import Origin
from apps.grade.poll.models.poll import Poll
from apps.grade.poll.models.section import SectionOrdering
from apps.grade.poll.models.template import Template
from apps.grade.poll.utils import getGroups, make_polls_for_groups
from apps.grade.ticket_create.models import StudentGraded
from django.core.exceptions import ObjectDoesNotExist
from apps.grade.ticket_create.utils import generate_keys_for_polls
from apps.users.models import Student, Employee

class Command(BaseCommand):
    args = '<semester( szablon)+>'
    help = 'tworzy ankiety na podstawie szablony'

    def handle(self, *args, **options):
        generate_keys_for_polls()