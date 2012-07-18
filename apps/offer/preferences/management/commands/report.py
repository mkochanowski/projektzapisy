from django.core.management.base import BaseCommand, CommandError
from apps.enrollment.courses.models.course import CourseEntity
from apps.enrollment.courses.models.course_type import Type
from apps.grade.ticket_create.models import StudentGraded
from django.core.exceptions import ObjectDoesNotExist
from apps.offer.proposal.models.proposal import Przedmiot
from apps.users.models import Student, Employee

class Command(BaseCommand):
    args = '<plik semester>'
    help = 'ocenia'

    def handle(self, *args, **options):
        courses = CourseEntity.get_proposals()

        for course in courses:
            print course.name
            for user in course.get_all_voters():
                print user.matricula

            print ' '

