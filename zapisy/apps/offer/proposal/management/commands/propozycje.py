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
        prz = Przedmiot.objects.all()

        n = {'176': 10, '146': 117, '1383': 119, '1403': 11, '3051': 73, '3050': 70, '2156': 67, '2664': 9, '1584': 54,'3055': 76, '1779': 119, '3034': 66, '2160': 2, '3052': 71, '2665': 12, '2161': 13, '150': 14, '1389': 119,'2157': 119, '2661': 15, '3054': 68, '3437': 94, '179': 16, '2662': 7, '187': 17, '183': 19, '589': 119,'171': 21, '149': 22, '3040': 81, '151': 23, '1404': 119, '147': 24, '1782': 119, '2163': 28, '154': 25,'1364': 26, '177': 29, '3053': 72, '162': 30, '145': 8, '2663': 33, '159': 31, '166': 34, '2148': 32,'1780': 35, '2330': 55, '163': 36, '1380': 37, '184': 38, '160': 119, '168': 39, '2109': 40, '186': 41,'1382': 53, '173': 42, '174': 43, '1385': 100, '3431': 75, '1583': 119, '1574': 3, '153': 44, '2340': 45,'1347': 119, '367': 114, '144': 82, '180': 108, '590': 47, '2158': 119, '1781': 48, '181': 49, '2668': 5,'1381': 50, '169': 51, '1378': 52, '2319': 80, '2106': 119, '528': 119, '1572': 6, '2329': 99, '152': 74,'595': 7}
        typ = {'1': 8, '2': 9, '3': 10, '4': 5, '5': 6, '6': 12, '7': 14, '8': 13, '9': 15, '10': 35}
        for p in prz:
            ce, created = CourseEntity.noremoved.get_or_create(name=p.nazwa[:100])

            id = n[str(p.kod_uz)] if str(p.kod_uz) in n else 119
            ce.owner     = Employee.objects.get(id = id)
            ce.shortName = ce.name[:30]
            ce.exam      = p.egzamin
            ce.english   = p.angielski
            ce.www       = p.strona_domowa
            ce.description = p.opis + '\n<br>' + p.wymagania + '\n<br>' + p.program + '\n<br>' +  p.literatura
            ce.type       = Type.objects.get(id= typ[str(p.rodzaj2007)])
            ce.save()

