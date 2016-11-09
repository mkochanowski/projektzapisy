# -*- coding: utf-8 -*-

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from apps.offer.vote.models.system_state import SystemState
from apps.users.models import Student


VOTE_LINK = '<a href="%s">głosuj</a>' % reverse('vote')


def create_active_system_state():
    SystemState.objects.create(
        vote_beg=timezone.now() - timezone.timedelta(10),
        vote_end=timezone.now() + timezone.timedelta(10),
    )


def create_inactive_system_state_in_past():
    SystemState.objects.create(
        vote_beg=timezone.now() - timezone.timedelta(30),
        vote_end=timezone.now() - timezone.timedelta(10),
    )


def create_inactive_system_state_in_future():
    SystemState.objects.create(
        vote_beg=timezone.now() + timezone.timedelta(30),
        vote_end=timezone.now() + timezone.timedelta(50),
    )


def create_and_login_student(testcase):
    user = User.objects.create_user('user', 'user@user.com', 'password')
    Student.objects.create(user=user)
    testcase.client.login(username='user', password='password')


def generic_voting_active_view_test_case(urlname, testcase):
    create_active_system_state()
    create_and_login_student(testcase)
    response = testcase.client.get(reverse(urlname))
    testcase.assertEquals(response.context['is_voting_active'], True)
    testcase.assertContains(response, VOTE_LINK, 1, html=True)


def _generic_voting_inactive_view_test_case(urlname, testcase):
    create_and_login_student(testcase)
    response = testcase.client.get(reverse(urlname))
    testcase.assertEquals(response.context['is_voting_active'], False)
    testcase.assertNotContains(response, VOTE_LINK, html=True)


def generic_voting_inactive_view_past_test_case(urlname, testcase):
    create_inactive_system_state_in_past()
    _generic_voting_inactive_view_test_case(urlname, testcase)


def generic_voting_inactive_view_future_test_case(urlname, testcase):
    create_inactive_system_state_in_future()
    _generic_voting_inactive_view_test_case(urlname, testcase)


class VoteViewTestCase(TestCase):
    def test_vote_link_when_system_is_active(self):
        generic_voting_active_view_test_case('vote-view', self)

    def test_vote_link_when_system_is_inactive_in_past(self):
        generic_voting_inactive_view_past_test_case('vote-view', self)

    def test_vote_link_when_system_is_inactive_in_future(self):
        generic_voting_inactive_view_future_test_case('vote-view', self)


class VoteSummaryViewTestCase(TestCase):
    def test_vote_link_when_system_is_active(self):
        generic_voting_active_view_test_case('vote-summary', self)

    def test_vote_link_when_system_is_inactive_in_past(self):
        generic_voting_inactive_view_past_test_case('vote-summary', self)

    def test_vote_link_when_system_is_inactive_in_future(self):
        generic_voting_inactive_view_future_test_case('vote-summary', self)
