from apps.notifications2.models import NotificationPreferences2
from django.forms import ModelForm


class NotificationForm(ModelForm):
    class Meta:
        model = NotificationPreferences2
        exclude = ['user']
