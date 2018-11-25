import random

from faker import Faker

from apps.theses.models import Thesis, ThesisKind, ThesisStatus
from apps.users.models import Employee, Student

NUM_THESES = 1000


fake = Faker()


def random_bool():
    return bool(random.getrandbits(1))


def random_title():
    return fake.name()


def random_advisor():
    return random.choice(Employee.objects.all())


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


def random_reserved():
    return random_bool()


def random_description():
    return fake.text()


def random_student():
    return random.choice(Student.objects.all())


def run():
    Thesis.objects.all().delete()
    for _ in range(NUM_THESES):
        Thesis.objects.create(
            title=random_title(),
            advisor=random_advisor(),
            auxiliary_advisor=random_advisor() if random_bool() else None,
            kind=random_kind(),
            status=random_status(),
            reserved=random_reserved(),
            description=random_description(),
            student=random_student(),
            student_2=random_student() if random_bool() else None
        )
    print(f'Created {NUM_THESES} instances')
