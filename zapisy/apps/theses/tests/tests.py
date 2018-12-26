import random
from typing import Dict

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import Group, User

from apps.users.models import Employee, Student, BaseUser
from apps.users.tests.factories import EmployeeFactory, StudentFactory
from ..models import Thesis, ThesisKind, ThesisStatus
from ..users import THESIS_BOARD_GROUP_NAME

from .factory_utils import (
    random_title, random_advisor, random_bool,
    random_kind, random_status, random_reserved,
    random_student, random_description,
)


class ThesesTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.create_users()
        cls.create_theses()

    @classmethod
    def create_users(cls):
        # Keep these numbers low - this is slow
        NUM_STUDENTS = 20
        NUM_EMPLOYEES = 15
        StudentFactory.create_batch(NUM_STUDENTS)
        EmployeeFactory.create_batch(NUM_EMPLOYEES)
        cls.students = list(Student.objects.all())
        cls.employees = list(Employee.objects.all())
        cls.board_group = Group.objects.get(name=THESIS_BOARD_GROUP_NAME)

        cls.staff_user = Employee.objects.all()[0]
        cls.staff_user.is_staff = True
        cls.staff_user.save()

        NUM_BOARD_MEMBERS = 7
        cls.board_members = []
        for i in range(1, 1 + NUM_BOARD_MEMBERS):
            member = Employee.objects.all()[i]
            cls.board_members.append(member)
            cls.board_group.user_set.add(member.user)

    @classmethod
    def create_theses(cls):
        cls.num_theses = random.randint(50, 100)
        studs = Student.objects.all()
        emps = Employee.objects.all()
        theses = [
            Thesis(
                title=random_title(),
                advisor=random_advisor(emps),
                auxiliary_advisor=random_advisor(emps) if random_bool() else None,
                kind=random_kind(),
                status=random_status(),
                reserved=random_reserved(),
                description=random_description(),
                student=random_student(studs),
                student_2=random_student(studs) if random_bool() else None
            ) for _ in range(cls.num_theses)
        ]
        Thesis.objects.bulk_create(theses)

    def login_as(self, user: BaseUser):
        self.client.login(username=user.user.username, password="test")

    def _test_user_can_list_theses(self, user: BaseUser):
        self.login_as(user)
        response = self.client.get(reverse("theses:theses-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), ThesesTestCase.num_theses)

    def test_logged_in_can_list_theses(self):
        self._test_user_can_list_theses(random.choice(ThesesTestCase.students))
        self._test_user_can_list_theses(random.choice(ThesesTestCase.employees))
        self._test_user_can_list_theses(random.choice(ThesesTestCase.board_members))
        self._test_user_can_list_theses(ThesesTestCase.staff_user)

    def test_logged_out_cannot_list_theses(self):
        self.client.logout()
        response = self.client.get(reverse("theses:theses-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def add_thesis(self, thesis_data: Dict):
        return self.client.post(reverse("theses:theses-list"), thesis_data, format="json")

    def test_employee_can_add_own_thesis(self):
        emp = random.choice(ThesesTestCase.employees)
        self.login_as(emp)
        thesis_data = {
            "title": random_title(),
            "advisor": {"id": emp.pk},
            "kind": random_kind(),
            "reserved": random_reserved(),
            "status": ThesisStatus.being_evaluated.value
        }
        response = self.add_thesis(thesis_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
