import random

from ..models import Thesis, ThesisStatus, ThesisKind
from ..views import ThesisTypeFilter
from .base import ThesesBaseTestCase, PAGE_SIZE
from .factory_utils import (
    random_current_status, random_available_status,
    random_status, make_employee_with_name
)


class ThesesFiltersAndSortingTestCase(ThesesBaseTestCase):
    """Tests the the filtering & sorting functionality works correctly"""
    def login_for_perms(self):
        """A simple helper that logs in as any user authorized to view theses
        so that we can test filters"""
        self.login_as(self.get_random_emp())

    def test_title_filter(self):
        num_matching = random.randint(1, PAGE_SIZE // 2)
        num_nonmatching = random.randint(1, PAGE_SIZE // 2)
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
        num_matching = random.randint(1, PAGE_SIZE // 2)
        num_nonmatching = random.randint(1, PAGE_SIZE // 2)
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
        num_normal = random.randint(1, PAGE_SIZE // 2)
        num_defended = random.randint(1, PAGE_SIZE // 2)
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
            self.assertNotEqual(thesis["status"], ThesisStatus.defended.value)

    def test_available_filter(self):
        """Test that the "available of type" filter works correctly"""
        num_matching_avail = random.randint(1, PAGE_SIZE // 3)
        num_matching_unavail = random.randint(1, PAGE_SIZE // 3)
        num_other = random.randint(1, PAGE_SIZE // 3)
        matching_avail = [
            self.make_thesis(
                kind=ThesisKind.bachelors,
                status=random_available_status(),
                reserved=False
            ) for i in range(num_matching_avail)
        ]
        matching_unavail = [
            self.make_thesis(
                kind=ThesisKind.bachelors,
                status=random_status() if i % 2 else ThesisStatus.in_progress,
                reserved=bool(i % 2)
            ) for i in range(num_matching_unavail)
        ]
        other = [
            self.make_thesis(kind=ThesisKind.isim) for i in range(num_other)
        ]
        Thesis.objects.bulk_create(matching_avail + matching_unavail + other)
        self.login_for_perms()
        theses = self.get_theses_with_data({"type": ThesisTypeFilter.available_bachelors.value})
        self.assertEqual(len(theses), num_matching_avail)
        for thesis in theses:
            self.assertEqual(thesis["kind"], ThesisKind.bachelors.value)
            self.assertNotEqual(thesis["status"], ThesisStatus.in_progress.value)
            self.assertNotEqual(thesis["status"], ThesisStatus.defended.value)
            self.assertFalse(thesis["reserved"])

    def test_title_sort(self):
        """Test that sorting by title works correctly"""
        current_titles = ["abc", "abd", "def", "zzz"]
        archived_titles = ["aaaa", "zyd"]
        currents = [
            self.make_thesis(title=cur_title, status=random_current_status())
            for cur_title in current_titles
        ]
        archiveds = [
            self.make_thesis(title=arch_title, status=ThesisStatus.defended)
            for arch_title in archived_titles
        ]
        all_theses = currents + archiveds
        Thesis.objects.bulk_create(random.sample(all_theses, len(all_theses)))
        self.login_for_perms()
        theses = self.get_theses_with_data({"column": "title", "dir": "asc"})
        self.assertEqual(len(theses), len(all_theses))
        all_titles = current_titles + archived_titles
        for i in range(len(all_theses)):
            self.assertEqual(theses[i]["title"], all_titles[i])

    def test_advisor_sort(self):
        """Test that sorting by advisor name works correctly"""
        current_adv_names = ["abc", "abd", "def", "zzz"]
        archived_adv_names = ["aaaa", "zyd"]
        currents = [
            self.make_thesis(
                advisor=make_employee_with_name(cur_adv_name),
                status=random_current_status()
            ) for cur_adv_name in current_adv_names
        ]
        archiveds = [
            self.make_thesis(
                advisor=make_employee_with_name(arch_adv_name),
                status=ThesisStatus.defended
            ) for arch_adv_name in archived_adv_names
        ]
        all_theses = currents + archiveds
        Thesis.objects.bulk_create(random.sample(all_theses, len(all_theses)))
        self.login_for_perms()
        theses = self.get_theses_with_data({"column": "advisor", "dir": "asc"})
        self.assertEqual(len(theses), len(all_theses))
        all_adv_names = current_adv_names + archived_adv_names
        for i in range(len(all_theses)):
            self.assertEqual(theses[i]["advisor"]["display_name"], all_adv_names[i])
