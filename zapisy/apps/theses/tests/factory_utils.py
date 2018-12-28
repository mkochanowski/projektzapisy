import random
from faker import Faker

from ..models import ThesisKind, ThesisStatus, ThesisVote


fake = Faker()


def random_bool():
    return bool(random.getrandbits(1))


def random_title():
    return fake.name()


def random_advisor(emps):
    return random.choice(emps)


def random_kind():
    return random.choice(list(ThesisKind))


def random_status():
    return random.choice([status for status in ThesisStatus])


def random_current_status():
    return random.choice([status for status in ThesisStatus if status != ThesisStatus.defended])


def random_available_status():
    return random.choice([
        ThesisStatus.accepted,
        ThesisStatus.being_evaluated,
        ThesisStatus.returned_for_corrections
    ])


def random_reserved():
    return random_bool()


def random_description():
    return fake.text()


def random_student(studs):
    return random.choice(studs)


def random_vote():
    return random.choice(list(ThesisVote))
