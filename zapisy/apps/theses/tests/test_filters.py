import random

from ..models import Thesis, ThesisStatus
from ..views import ThesisTypeFilter
from .base import ThesesBaseTestCase, PAGE_SIZE
from .factory_utils import random_current_status


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
        nonmatching_emp = self.get_random_emp_different_from(matching_emp)
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
