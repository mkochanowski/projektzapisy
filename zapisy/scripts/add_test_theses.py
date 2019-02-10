import random
from datetime import date, timedelta

from faker import Faker

from apps.theses.models import Thesis, ThesisKind, ThesisStatus
from apps.users.models import Employee, Student

NUM_THESES = 1000


fake = Faker()


def random_bool():
    return bool(random.getrandbits(1))


def random_title():
    return f'{fake.name()}_{random.randrange(123123)}'


def random_advisor(emps):
    return random.choice(emps)


valid_kinds = [
    kind.value for kind in ThesisKind
]
def random_kind():  # noqa: E302
    return random.choice(valid_kinds)


valid_statuses = [
    status.value for status in ThesisStatus
]
def random_status():  # noqa: E302
    return random.choice(valid_statuses)


def random_reserved_until():
    return date.today() + timedelta(days=random.randrange(100))


def random_description():
    return fake.text()


def random_student(studs):
    return random.choice(studs)


def run():
    Thesis.objects.all().delete()
    studs = Student.objects.all()
    emps = Employee.objects.all()
    theses = [
        Thesis(
            title=random_title(),
            advisor=random_advisor(emps),
            auxiliary_advisor=random_advisor(emps) if random_bool() else None,
            kind=random_kind(),
            status=ThesisStatus.BEING_EVALUATED.value,
            reserved_until=random_reserved_until() if random_bool() else None,
            description=random_description(),
            student=random_student(studs),
            student_2=random_student(studs) if random_bool() else None
        ) for _ in range(NUM_THESES)
    ]
    Thesis.objects.bulk_create(theses)
    print(f'Created {NUM_THESES} instances')
