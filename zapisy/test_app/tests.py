# -*- coding: utf-8-*-

# Run this tests with 'xvfb-run python manage.py test test_app' command

from django.test import LiveServerTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from django.contrib.auth.models import User
from apps.users.models import Employee, Student
from apps.enrollment.courses.models import Semester, CourseEntity, Course, Type
from apps.offer.vote.models import SystemState

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from collections import defaultdict


class SeleniumTestCase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTestCase, cls).tearDownClass()


class NewSemesterTests(SeleniumTestCase):

    def setUp(self):
        self.password = '11111'
        self.admin = User.objects.create_superuser(username='przemka', 
                                              password=self.password,
                                              email='admin@admin.com')
        self.admin.first_name = 'przemka'
        self.admin.save()
        self.employee = Employee.objects.create(user=self.admin)
        user_student1 = User.objects.create_user(username='student1', password=self.password)
        user_student2 = User.objects.create_user(username='student2', password=self.password)
        user_student3 = User.objects.create_user(username='student3', password=self.password)
        user_student4 = User.objects.create_user(username='student4', password=self.password)
        self.student1 = Student.objects.create(user=user_student1, matricula="264823")
        self.student2 = Student.objects.create(user=user_student2, matricula="222222")
        self.student3 = Student.objects.create(user=user_student3, matricula="333333")
        self.student4 = Student.objects.create(user=user_student4, matricula="444444")

        self.course_type = Type.objects.create(name='Informatyczny')
        for i in range(1, 6):
            CourseEntity.objects.create(
                name='Course %s' % i,
                semester='z',
                type=self.course_type,
                status=1 # w ofercie
            )
        for i in range(6, 11):
            CourseEntity.objects.create(
                name='Course %s' % i,
                semester='l',
                type=self.course_type,
                status=1 # w ofercie
            )

        CourseEntity.objects.create(
            name='Course 50',
            semester='l',
            type=self.course_type,
            status=0 # propozycja
        )

        CourseEntity.objects.create(
            name='Course 100',
            semester='z',
            type=self.course_type,
            status=1 # w ofercie
        )

        CourseEntity.objects.create(
            name='Course 101',
            semester='l',
            type=self.course_type,
            status=1 # w ofercie
        )

        for course_entity in CourseEntity.objects.all():
            course_entity.owner = self.employee
            course_entity.save()

        self.winter_courses = ['Course 1', 'Course 2', 'Course 3']

        self.current_semester = Semester.objects.create(
            type=Semester.TYPE_SUMMER,
            year='1',                               
            semester_beginning=date.today(),
            semester_ending=date.today() + relativedelta(months=3),
            records_ects_limit_abolition=date.today() + relativedelta(days=10)
        )


        self.next_winter_semester = Semester.objects.create(
            type=Semester.TYPE_WINTER,
            year='2',
            semester_beginning=self.current_semester.semester_ending + relativedelta(days=1),
            semester_ending=self.current_semester.semester_ending + relativedelta(days=1, months=3),
            records_ects_limit_abolition=self.current_semester.semester_ending + relativedelta(days=11)
        )

        self.next_summer_semester = Semester.objects.create(
            type=Semester.TYPE_SUMMER,
            year='3',
            semester_beginning=self.next_winter_semester.semester_ending + relativedelta(days=1),
            semester_ending=self.next_winter_semester.semester_ending + relativedelta(days=1, months=3),
            records_ects_limit_abolition=self.next_winter_semester.semester_ending + relativedelta(days=11)
        )

        self.system_state = SystemState.objects.create(
            semester_winter=self.next_winter_semester,
            semester_summer=self.next_summer_semester,
            max_points=12,
            max_vote=3
        )


    def test_new_semester_scenario(self):
        self.prepare_course_entities_for_voting()
        self.perform_voting()
        self.create_offer_for_winter_semester()
        self.perform_winter_correction()

        self.selenium.get_screenshot_as_file("screenshot.png")

    def prepare_course_entities_for_voting(self):
        self.selenium.get('%s%s' % (self.live_server_url, '//'))
        self.selenium.find_element_by_id('id_login').send_keys(self.admin.username)
        self.selenium.find_element_by_id('id_password').send_keys(self.password)
        self.selenium.find_element_by_xpath('//button[contains(text(), "Loguj")]').click()
        self.selenium.find_element_by_link_text('Oferta').click()
        self.selenium.get('%s%s' % (self.selenium.current_url, '/manage/proposals'))
        self.selenium.find_element_by_link_text('Głosowanie').click()

        nonselected_select = Select(
            WebDriverWait(self.selenium, 1).until(EC.element_to_be_clickable((By.ID, 'bootstrap-duallistbox-nonselected-list_for_voting')))
        )
        # nonselected_select = Select(self.selenium.find_element_by_id('bootstrap-duallistbox-nonselected-list_for_voting'))
        selected_select = Select(self.selenium.find_element_by_id('bootstrap-duallistbox-selected-list_for_voting'))
        self.assertEqual(CourseEntity.objects.filter(status=1).count(), len(nonselected_select.options))
        self.assertEqual(CourseEntity.objects.filter(status=3).count(), len(selected_select.options))

        for ce in CourseEntity.objects.filter(status=1):
            if ce.name != 'Course 100' and ce.name != 'Course 101':
                nonselected_select.select_by_visible_text(ce.name)

        self.selenium.find_element_by_xpath('//input[@value="Zapisz"]').click()

        nonselected_select = Select(self.selenium.find_element_by_id('bootstrap-duallistbox-nonselected-list_for_voting'))
        selected_select = Select(self.selenium.find_element_by_id('bootstrap-duallistbox-selected-list_for_voting'))
        self.assertEqual(CourseEntity.objects.filter(status=1).count(), len(nonselected_select.options))
        self.assertEqual(CourseEntity.objects.filter(status=3).count(), len(selected_select.options))

    def perform_voting(self):
        # voting starts
        self.system_state.vote_beg = date.today()
        self.system_state.vote_end = date.today() + relativedelta(days=1)
        self.system_state.save()

        self.results_points = defaultdict(int)
        self.results_votes = defaultdict(int)
        self.vote(
            self.student1, 
            {'Course 1': 3, 'Course 2': 3, 'Course 3': 3, 'Course 4': 3, 
             'Course 5': 3, 'Course 6': 3, 'Course 7': 3, 'Course 8': 3,
             'Course 9': 3, 'Course 10': 3}
        )
        self.vote(
            self.student1, 
            {'Course 1': 1, 'Course 2': 2, 'Course 4': 3, 'Course 5': 2,
             'Course 6': 2, 'Course 7': 1 ,'Course 8': 1}
        )
        self.vote(
            self.student2, 
            {'Course 1': 2, 'Course 2': 1, 'Course 3': 3, 'Course 4': 2,
             'Course 8': 1, 'Course 9': 1, 'Course 10': 2}
        )
        self.vote(
            self.student3, 
            {'Course 1': 3, 'Course 3': 1, 'Course 4': 2, 'Course 6': 2,
             'Course 8': 2, 'Course 10': 2}
        )
        self.vote(
            self.student4,
            {'Course 2': 1, 'Course 3': 2, 'Course 5': 2, 'Course 7': 3,
             'Course 8': 1, 'Course 9': 1, 'Course 10': 2}
        )

        # check voting results
        self.selenium.find_element_by_link_text('Głosowanie').click()
        self.selenium.find_element_by_link_text('Podsumowanie głosowania').click()
        rows = self.selenium.find_elements_by_xpath('//table/tbody/tr')
        for row in rows:
            cells = row.find_elements_by_tag_name('td')
            self.assertEqual(self.results_points[cells[0].text], int(cells[1].text))
            self.assertEqual(self.results_votes[cells[0].text], int(cells[2].text))

        # voting ends
        self.system_state.vote_beg = date.today() - relativedelta(days=2)
        self.system_state.vote_end = date.today() - relativedelta(days=1)
        self.system_state.save()


    def vote(self, student, points):
        self.selenium.get('%s%s' % (self.live_server_url, '/users/logout/'))
        self.selenium.get('%s%s' % (self.live_server_url, '//'))
        self.selenium.find_element_by_id('id_login').send_keys(student.user.username)
        self.selenium.find_element_by_id('id_password').send_keys(self.password)
        self.selenium.find_element_by_xpath('//button[contains(text(), "Loguj")]').click()
        self.selenium.find_element_by_link_text('Oferta').click()
        self.selenium.find_element_by_link_text('Głosowanie').click()
        WebDriverWait(self.selenium, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Głosuj'))).click()
        # self.selenium.find_element_by_link_text('Głosuj').click()

        sum_points = sum(points.itervalues())

        for course_name, value in points.iteritems():
            select = Select(self.selenium.find_element_by_xpath('//li[label/a[text()="%s"]]/select' % course_name))
            select.select_by_value(str(value))
            if sum_points <= self.system_state.max_points:
                self.results_points[course_name] += value
                self.results_votes[course_name] += 1

        self.selenium.find_element_by_xpath('//input[@value="Głosuj"]').click()

        if sum_points <= self.system_state.max_points:
            self.assertEqual(len(self.selenium.find_elements_by_xpath('//div[contains(text(), "Oddano poprawny głos")]')), 1)
        else:
            self.assertEqual(len(self.selenium.find_elements_by_xpath('//div[contains(text(), "Nie udało się oddać głosu")]')), 1)
        
    def create_offer_for_winter_semester(self):
        for course in self.winter_courses:
            Course.objects.create(
                entity=CourseEntity.objects.get(name=course),
                semester=self.next_winter_semester
            )

    def perform_winter_correction(self):
        # winter correction starts
        self.system_state.winter_correction_beg = date.today()
        self.system_state.winter_correction_end = date.today() + relativedelta(days=1)
        self.system_state.save()

        self.correction(
            self.student1, 
            {'Course 1': 3, 'Course 3': 3}
        )
        self.correction(
            self.student2, 
            {'Course 2': 3}
        )
        self.correction(
            self.student3, 
            {'Course 2': 2}
        )
        self.correction(
            self.student4,
            {'Course 1': 1, 'Course 2': 2}
        )

        # winter correction ends
        self.system_state.winter_correction_beg = date.today() - relativedelta(days=2)
        self.system_state.winter_correction_end = date.today() - relativedelta(days=1)
        self.system_state.save()


    def correction(self, student, points):
        self.selenium.get('%s%s' % (self.live_server_url, '/users/logout/'))
        self.selenium.get('%s%s' % (self.live_server_url, '//'))
        self.selenium.find_element_by_id('id_login').send_keys(student.user.username)
        self.selenium.find_element_by_id('id_password').send_keys(self.password)
        self.selenium.find_element_by_xpath('//button[contains(text(), "Loguj")]').click()
        self.selenium.find_element_by_link_text('Oferta').click()
        self.selenium.find_element_by_link_text('Głosowanie').click()
        WebDriverWait(self.selenium, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Głosuj'))).click()
        # self.selenium.find_element_by_link_text('Głosuj').click()

        for course_name, value in points.iteritems():
            select = Select(self.selenium.find_element_by_xpath('//li[label/a[text()="%s"]]/select' % course_name))
            select.select_by_value(str(value))

        self.selenium.find_element_by_xpath('//input[@value="Głosuj"]').click()


