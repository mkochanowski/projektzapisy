from django.core.management.base import BaseCommand, CommandError
from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models.origin import Origin
from apps.grade.poll.models.poll import Poll
from apps.grade.poll.models.section import SectionOrdering
from apps.grade.poll.models.template import Template
from apps.grade.poll.utils import getGroups, make_polls_for_groups
from apps.grade.ticket_create.models import StudentGraded
from django.core.exceptions import ObjectDoesNotExist
from apps.users.models import Student, Employee

class Command(BaseCommand):
    args = '<semester( szablon)+>'
    help = 'tworzy ankiety na podstawie szablony'

    def handle(self, *args, **options):
        semester  = Semester.objects.get(id=args[0])
        print semester
        templates = Template.objects.filter(pk__in=args[1:])
        prych     = Employee.objects.get(user__pk=43)
        for template in templates:
            t = dict(
                    type           = None if template.group_type == '--' else template.group_type,
                    sections       = template.sections.all(),
                    studies_type   = template.studies_type,
                    title          = template.title,
                    description    = template.description,
                    course         = template.course,
                    exam           = template.exam,
                    semester       = semester,
                    groups_without = 'off',
                    group          = None)
            groups   = getGroups({}, t)
            origin = Origin()
            origin.save()

            if groups:
                for group in groups:
                    if t['groups_without'] == 'on' and Poll.get_all_polls_for_group(group, semester).count()>0:
                        continue

                    poll = Poll()
                    poll.author       = prych
                    poll.title        = t['title']
                    poll.description  = t['description']
                    poll.semester     = t['semester']
                    poll.group        = group
                    poll.studies_type = t['studies_type']
                    poll.origin = origin
                    poll.save()

                    if 'sections' in t:
                            sections = t['sections']

                            for section in sections:
                                pollSection = SectionOrdering()
                                pollSection.poll = poll
                                pollSection.position = section.pk
                                pollSection.section = section
                                pollSection.save()

            else:
                poll = Poll()
                poll.author       = prych
                poll.title        = t['title']
                poll.description  = t['description']
                poll.semester     = t['semester']
                poll.group        = None
                poll.studies_type = t['studies_type']
                poll.origin = origin
                poll.save()
