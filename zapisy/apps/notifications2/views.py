from datetime import datetime

from django.shortcuts import render
from django.contrib import messages

from apps.users.models import BaseUser
from apps.notifications2.forms import PreferencesFormStudent, PreferencesFormTeacher
from apps.notifications2.models import NotificationPreferencesStudent, NotificationPreferencesTeacher
from apps.notifications2.repositories import get_notifications_repository
from apps.notifications2.utils import render_description

from libs.ajax_messages import AjaxFailureMessage


def index(request):
    if not request.user.is_authenticated:
        return AjaxFailureMessage.auto_render(
            'NotAuthenticated', 'Nie jesteś zalogowany.', request)

    repo = get_notifications_repository()

    notifications = [
        render_description(notification.description_id, notification.description_args)
        for notification in repo.get_all_for_user(request.user)
    ]

    repo.remove_all_older_than(request.user, datetime.now())

    return render(request, 'notifications2/index.html', {'notifications': notifications})


def FormView(request):
    if not request.user.is_authenticated:
        return AjaxFailureMessage.auto_render(
            'NotAuthenticated', 'Nie jesteś zalogowany.', request)

    if request.method == "POST":
        form = create_form(request)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return render(request, 'notifications2/pref.html', {'form': form})
        else:
            messages.error(request, "Wystąpił błąd, zmiany nie zostały zapisane. Proszę wypełnić formularz ponownie")
    else:
        form = create_form(request)

    return render(request, 'notifications2/pref.html', {'form': form})


def create_form(request):
    if BaseUser.is_employee(request.user):
        instance, created = NotificationPreferencesTeacher.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            return PreferencesFormTeacher(request.POST, instance=instance)
        return PreferencesFormTeacher(instance=instance)

    instance, created = NotificationPreferencesStudent.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        return PreferencesFormStudent(request.POST, instance=instance)
    return PreferencesFormStudent(instance=instance)
