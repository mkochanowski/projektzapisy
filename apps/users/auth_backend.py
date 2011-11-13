from django.contrib.auth.backends import ModelBackend
from apps.users.models import ExtendedUser

class ExtendedUserModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = ExtendedUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except ExtendedUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return ExtendedUser.objects.get(pk=user_id)
        except ExtendedUser.DoesNotExist:
            return None
