from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class BetterBackend(ModelBackend):

    def get_user(self, user_id):
        if hasattr(self, '__cached_user'):
            return self.__cached_user
        try:
            self.__cached_user = User.objects.select_related('student', 'employee').get(pk=user_id)
            return self.__cached_user
        except User.DoesNotExist:
            return None