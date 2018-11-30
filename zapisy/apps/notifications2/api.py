from datetime import datetime
from typing import Dict

from django.contrib.auth.models import User

from apps.notifications2.datatypes import Notification
from apps.notifications2.repositories import get_notifications_repository


def notify_user(user: User, description_id: str, description_dict: Dict):
    repo = get_notifications_repository()

    repo.save(
        user, Notification(datetime.now(), description_id, description_dict))
