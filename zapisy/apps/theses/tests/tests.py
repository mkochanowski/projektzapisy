import random
from typing import Dict

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import Group

from apps.users.models import Employee, Student, BaseUser
from apps.users.tests.factories import EmployeeFactory, StudentFactory
from ..models import Thesis, ThesisStatus
from ..views import ThesisTypeFilter
from ..users import THESIS_BOARD_GROUP_NAME

from .factory_utils import (
    random_title, random_bool,
    random_kind, random_status, random_reserved,
    random_description, random_current_status
)

PAGE_SIZE = 100


class ThesesBaseTestCase(APITestCase):
    """A test case base class for theses tests that takes care of user creation
    and provides common utilities
    """
    @classmethod
    def setUpTestData(cls):
        cls.create_users()

    NUM_BOARD_MEMBERS = 7

    @classmethod
    def create_users(cls):
        NUM_STUDENTS = 15
        NUM_EMPLOYEES = cls.NUM_BOARD_MEMBERS * 2
        StudentFactory.create_batch(NUM_STUDENTS)
        EmployeeFactory.create_batch(NUM_EMPLOYEES)
        cls.students = list(Student.objects.all())
        cls.employees = list(Employee.objects.all())
        cls.board_group = Group.objects.get(name=THESIS_BOARD_GROUP_NAME)

        cls.staff_user = Employee.objects.all()[0]
        cls.staff_user.is_staff = True
        cls.staff_user.save()

        cls.board_members = []
        for i in range(1, 1 + cls.NUM_BOARD_MEMBERS):
            member = Employee.objects.all()[i]
            cls.board_members.append(member)
            cls.board_group.user_set.add(member.user)

    @classmethod
    def get_random_emp(cls):
        return random.choice(cls.employees[1 + cls.NUM_BOARD_MEMBERS:])

    @classmethod
    def get_admin(cls):
        return cls.staff_user

    @classmethod
    def get_random_board_member(cls):
        return random.choice(cls.board_members)

    @classmethod
    def get_random_student(cls):
        return random.choice(cls.students)

    @classmethod
    def make_thesis(cls, **kwargs):
        """Create a thesis instance using the provided params or defaults"""
        return Thesis(
            title=kwargs.get("title", random_title()),
            advisor=kwargs.get("advisor", cls.get_random_emp()),
            auxiliary_advisor=kwargs.get(
                "auxiliary_advisor", cls.get_random_emp() if random_bool() else None
            ),
            kind=kwargs.get("kind", random_kind()).value,
            status=kwargs.get("status", random_status()).value,
            reserved=kwargs.get("reserved", random_reserved()),
            description=kwargs.get("description", random_description()),
            student=kwargs.get("student", cls.get_random_student()),
            student_2=kwargs.get("student_2", cls.get_random_student() if random_bool() else None)
        )

    def login_as(self, user: BaseUser):
        """Login as the specified user"""
        self.client.login(username=user.user.username, password="test")

    def get_response_with_data(self, data={}):
        """Make a request to the theses list endpoint with the specified params,
        return the raw response
        """
        url = reverse("theses:theses-list")
        if "limit" not in data:
            data["limit"] = PAGE_SIZE
        return self.client.get(url, data)

    def get_theses_with_data(self, data={}):
        """Download theses with the provided params, then deserialize"""
        data = self.get_response_with_data(data).data
        return data["results"]


class ThesesListingTestCase(ThesesBaseTestCase):
    """Tests theses listing functionality: is the limit setting respected,
    are permissions granted correctly"""
    @classmethod
    def setUpTestData(cls):
        super(ThesesListingTestCase, cls).setUpTestData()
        cls.create_theses()

    @classmethod
    def create_theses(cls):
        cls.num_theses = random.randint(PAGE_SIZE, PAGE_SIZE * 2)
        theses = [cls.make_thesis() for _ in range(cls.num_theses)]
        Thesis.objects.bulk_create(theses)

    def _check_theses_response_data(self, data):
        self.assertTrue(isinstance(data, dict))
        self.assertTrue("count" in data)
        self.assertTrue("results" in data)
        results = data["results"]
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), PAGE_SIZE)

    def _test_user_can_list_theses(self, user: BaseUser):
        self.login_as(user)
        response = self.get_response_with_data()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_theses_response_data(response.data)

    def test_logged_in_can_list_theses(self):
        self._test_user_can_list_theses(self.get_random_student())
        self._test_user_can_list_theses(self.get_random_emp())
        self._test_user_can_list_theses(self.get_random_board_member())
        self._test_user_can_list_theses(self.get_admin())

    def test_logged_out_cannot_list_theses(self):
        response = self.client.get(reverse("theses:theses-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ThesesFiltersTestCase(ThesesBaseTestCase):
    def login_for_perms(self):
        """A simple helper that logs in as any user authorized to view theses
        so that we can test filters"""
        self.login_as(self.get_random_emp())

    def test_title_filter(self):
        num_matching = random.randint(10, PAGE_SIZE / 2)
        num_nonmatching = random.randint(10, PAGE_SIZE / 2)
        title_base_match = "foobar"
        title_base_nonmatch = "{}blahblah"
        theses_matching = [
            self.make_thesis(title=f'{title_base_match}_{i}') for i in range(num_matching)
        ]
        theses_nonmatching = [
            self.make_thesis(title=title_base_nonmatch.format(i)) for i in range(num_nonmatching)
        ]
        Thesis.objects.bulk_create(theses_matching + theses_nonmatching)
        self.login_for_perms()
        theses = self.get_theses_with_data({"title": title_base_match})
        self.assertEqual(len(theses), num_matching)
        for thesis in theses:
            self.assertTrue(title_base_match in thesis["title"])

    def test_advisor_filter(self):
        num_matching = random.randint(1, PAGE_SIZE / 2)
        num_nonmatching = random.randint(1, PAGE_SIZE / 2)
        matching_emp = self.get_random_emp()
        nonmatching_emp = self.get_random_emp()
        while matching_emp == nonmatching_emp:
            nonmatching_emp = self.get_random_emp()
        theses_matching = [
            self.make_thesis(advisor=matching_emp) for i in range(num_matching)
        ]
        theses_nonmatching = [
            self.make_thesis(advisor=nonmatching_emp) for i in range(num_nonmatching)
        ]
        Thesis.objects.bulk_create(theses_matching + theses_nonmatching)
        self.login_for_perms()
        theses = self.get_theses_with_data({"advisor": matching_emp.get_full_name()})
        self.assertEqual(len(theses), num_matching)
        for thesis in theses:
            self.assertTrue(matching_emp.get_full_name() in thesis["advisor"]["display_name"])

    def test_current_type_filter(self):
        """Test that current, i.e. not yet defended theses are being filtered correctly"""
        num_normal = random.randint(1, PAGE_SIZE / 2)
        num_defended = random.randint(1, PAGE_SIZE / 2)
        normal = [
            self.make_thesis(status=random_current_status()) for i in range(num_normal)
        ]
        defended = [
            self.make_thesis(status=ThesisStatus.defended) for i in range(num_defended)
        ]
        Thesis.objects.bulk_create(normal + defended)
        self.login_for_perms()
        theses = self.get_theses_with_data({"type": ThesisTypeFilter.all_current.value})
        self.assertEqual(len(theses), num_normal)
        for thesis in theses:
            self.assertTrue(thesis["status"] != ThesisStatus.defended.value)


class ThesesModificationTestCase(ThesesBaseTestCase):
    def add_thesis(self, thesis_data: Dict):
        return self.client.post(reverse("theses:theses-list"), thesis_data, format="json")

    def test_employee_can_add_own_thesis(self):
        emp = self.get_random_emp()
        self.login_as(emp)
        thesis_data = {
            "title": random_title(),
            "advisor": {"id": emp.pk},
            "kind": random_kind().value,
            "reserved": random_reserved(),
            "status": ThesisStatus.being_evaluated.value
        }
        response = self.add_thesis(thesis_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
