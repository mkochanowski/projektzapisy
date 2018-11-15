from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from django.contrib.auth.models import User

from apps.notifications2.datatypes import Notification


def get_current_repository_implementation() -> NotificationsRepository:
    """
    Return an object implementing NotificationsRepository interface,
    thus providing access to _some_ notifications storage.
    Client code should always call this method instead of
    instantiating such classes directly.
    TODO: replace it with Redis-based one when it's ready
    """

    return FakeNotificationsRepository()


class NotificationsRepository(ABC):

    @abstractmethod
    def get_count_for_user(self, user: User) -> int:
        pass

    @abstractmethod
    def get_all_for_user(self, user: User) -> List[Notification]:
        pass

    @abstractmethod
    def get_unsent_for_user(self, user: User) -> List[Notification]:
        pass

    @abstractmethod
    def save(self, user: User, notification: Notification) -> None:
        pass

    @abstractmethod
    def mark_all_before_as_read(self, user: User, until: datetime) -> None:
        pass


class FakeNotificationsRepository(NotificationsRepository):

    def __init__(self):
        self.notifications = [
            Notification(datetime.now(), 'fake_desc', {'example_arg': 'aaa'}),
            Notification(datetime.now(), 'fake_desc', {'example_arg': 'bbb'}),
            Notification(datetime.now(), 'fake_desc', {'example_arg': 'ccc'}),
        ]

    def get_count_for_user(self, user: User) -> int:
        return 3

    def get_all_for_user(self, user: User) -> List[Notification]:
        return self.notifications

    def get_unsent_for_user(self, user: User) -> List[Notification]:
        return self.notifications

    def save(self, user: User, notification: Notification) -> None:
        pass

    def mark_all_before_as_read(self, user: User, until: datetime) -> None:
        pass
