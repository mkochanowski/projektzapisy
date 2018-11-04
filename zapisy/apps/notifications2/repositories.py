from abc import ABC, abstractmethod
from datetime import datetime

from django.contrib.auth.models import User

from apps.notifications2.datatypes import Notification


class NotificationsRepository(ABC):

    @abstractmethod
    def get_count_for_user(self, user: User):
        pass

    @abstractmethod
    def get_all_for_user(self, user: User):
        pass

    @abstractmethod
    def save(self, user: User, notification: Notification):
        pass

    @abstractmethod
    def mark_all_before_as_read(self, user: User, until: datetime):
        pass


class FakeNotificationsRepository(NotificationsRepository):

    def __init__(self):
        self.notifications = [
            Notification(datetime.now(), 'fake_desc', {'example_arg': 'aaa'}),
            Notification(datetime.now(), 'fake_desc', {'example_arg': 'bbb'}),
            Notification(datetime.now(), 'fake_desc', {'example_arg': 'ccc'}),
        ]

    def get_count_for_user(user: User):
        return 3

    def get_all_for_user(user: User):
        return self.notifications

    def save(self, user: User, notification: Notification):
        pass

    def mark_all_before_as_read(self, user: User, until: datetime):
        pass
