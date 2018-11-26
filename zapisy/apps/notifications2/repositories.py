from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from django.conf import settings
from django.contrib.auth.models import User
import redis

from apps.notifications2.datatypes import Notification
from apps.notifications2.serialization import NotificationSerializer


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
    def remove_all_older_than(self, user: User, until: datetime) -> int:
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

    def remove_all_older_than(self, user: User, until: datetime) -> int:
        return 0


class RedisNotificationsRepository(NotificationsRepository):

    def __init__(self, serializer: NotificationSerializer):
        self.serializer = serializer
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASS)
        self.removed_count = 0

    def get_count_for_user(self, user: User) -> int:
        # SCARD returns 0 if one of them does not exist
        # so no need to check for key existence here
        unsent_count = self.redis_client.scard(
            self._generate_unsent_key_for_user(user))
        sent_count = self.redis_client.scard(
            self._generate_sent_key_for_user(user))

        return unsent_count + sent_count

    def get_all_for_user(self, user: User) -> List[Notification]:
        serialized = self.redis_client.smembers(
            self._generate_unsent_key_for_user(user))
        serialized = serialized.union(
            self.redis_client.smembers(self._generate_sent_key_for_user(user)))

        return list(map(self.serializer.deserialize, serialized))

    def get_unsent_for_user(self, user: User) -> List[Notification]:
        return list(map(
            self.serializer.deserialize,
            self.redis_client.smembers(self._generate_unsent_key_for_user(user))))

    def save(self, user: User, notification: Notification) -> None:
        self.redis_client.sadd(
            self._generate_unsent_key_for_user(user),
            self.serializer.serialize(notification))

    def remove_all_older_than(self, user: User, until: datetime) -> int:
        self.removed_count = 0

        self._remove_all_older_than(
            self._generate_unsent_key_for_user(user), until)
        self._remove_all_older_than(
            self._generate_sent_key_for_user(user), until)

        return self.removed_count

    def _remove_all_older_than(self, key: str, point_in_time: datetime) -> int:
        notifications_under_that_key = map(
            self.serializer.deserialize,
            self.redis_client.smembers(key))

        for notification in notifications_under_that_key:
            if notification.issued_on < point_in_time:
                self.redis_client.srem(
                    key, self.serializer.serialize(notification))
                self.removed_count += 1

    def _generate_unsent_key_for_user(self, user: User) -> str:
        return f'notifications:unsent#{user.id}'

    def _generate_sent_key_for_user(self, user: User) -> str:
        return f'notifications:sent#{user.id}'


def get_notifications_repository() -> NotificationsRepository:
    """
    Return an object implementing NotificationsRepository interface,
    thus providing access to _some_ notifications storage.
    Client code should always call this method instead of
    instantiating such classes directly.
    TODO: replace it with Redis-based one when it's ready
    """

    return FakeNotificationsRepository()
