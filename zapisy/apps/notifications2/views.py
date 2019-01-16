from apps.notifications2.forms import NotificationForm
from apps.notifications2.models import NotificationPreferences2
from datetime import datetime
from django.shortcuts import render
from apps.notifications2.repositories import get_notifications_repository
from apps.notifications2.utils import render_description
from django.contrib import messages


def index(request):

    repo = get_notifications_repository()

    notifications = [
        render_description(notification.description_id, notification.description_args)
        for notification in repo.get_all_for_user(request.user)
    ]

    repo.remove_all_older_than(request.user, datetime.now())

    return render(request, 'notifications2/index.html', {'notifications': notifications})


def FormView(request):
    if request.method == "POST":
        try:
            item = NotificationPreferences2.objects.get(user=request.user)
            form = NotificationForm(request.POST, instance=item)
        except NotificationPreferences2.DoesNotExist:
            form = NotificationForm(request.POST)

        if not form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            args = {'form': form}
            return render(request, 'notifications2/pref.html', args)
        else:
            messages.error(request, "Wystąpił błąd, zmiany nie zostały zapisane. Proszę wypełnić formularz ponownie")
    else:
        try:
            item = NotificationPreferences2.objects.get(user=request.user)
            form = NotificationForm(instance=item)
        except NotificationPreferences2.DoesNotExist:
            form = NotificationForm()

    args = {'form': form}
    return render(request, 'notifications2/pref.html', args)
