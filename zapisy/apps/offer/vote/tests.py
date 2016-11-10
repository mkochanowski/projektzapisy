# -*- coding: utf-8 -*-

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from apps.offer.vote.models.system_state import SystemState
from apps.users.models import Student


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


class VoteLinkTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.VOTE_LINK = '<a href="%s">głosuj</a>' % reverse('vote')
        user = User.objects.create_user('user', 'user@user.com', 'password')
        Student.objects.create(user=user)

    def setUp(self):
        self.client.login(username='user', password='password')

    def generic_voting_active_view_test_case(self, urlname):
        create_active_system_state()
        response = self.client.get(reverse(urlname))
        self.assertEquals(response.context['is_voting_active'], True)
        self.assertContains(response, self.VOTE_LINK, 1, html=True)

    def _generic_voting_inactive_view_test_case(self, urlname):
        response = self.client.get(reverse(urlname))
        self.assertEquals(response.context['is_voting_active'], False)
        self.assertNotContains(response, self.VOTE_LINK, html=True)

    def generic_voting_inactive_view_past_test_case(self, urlname):
        create_inactive_system_state_in_past()
        self._generic_voting_inactive_view_test_case(urlname)

    def generic_voting_inactive_view_future_test_case(self, urlname):
        create_inactive_system_state_in_future()
        self._generic_voting_inactive_view_test_case(urlname)

    def test_vote_link_in_vote_view_when_system_is_active(self):
        self.generic_voting_active_view_test_case('vote-view')

    def test_vote_link_in_vote_view_when_system_is_inactive_in_past(self):
        self.generic_voting_inactive_view_past_test_case('vote-view')

    def test_vote_link_in_vote_view_when_system_is_inactive_in_future(self):
        self.generic_voting_inactive_view_future_test_case('vote-view')

    def test_vote_link_in_vote_summary_when_system_is_active(self):
        self.generic_voting_active_view_test_case('vote-summary')

    def test_vote_link_in_vote_summary_when_system_is_inactive_in_past(self):
        self.generic_voting_inactive_view_past_test_case('vote-summary')

    def test_vote_link_in_vote_summary_when_system_is_inactive_in_future(self):
        self.generic_voting_inactive_view_future_test_case('vote-summary')
