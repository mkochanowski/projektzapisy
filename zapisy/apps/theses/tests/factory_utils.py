import random
from faker import Faker

from ..models import ThesisKind, ThesisStatus


fake = Faker()


def random_bool():
    return bool(random.getrandbits(1))


def random_title():
    return fake.name()


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


def random_reserved():
    return random_bool()


def random_description():
    return fake.text()


def random_student(studs):
    return random.choice(studs)
