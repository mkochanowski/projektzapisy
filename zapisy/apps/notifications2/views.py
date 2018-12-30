from datetime import datetime

from django.shortcuts import render
from django import forms

from apps.notifications2.repositories import get_notifications_repository
from apps.notifications2.utils import render_description
from apps.notifications2.models import NotificationForm

def index(request):

    repo = get_notifications_repository()

    notifications = [
        render_description(notification.description_id, notification.description_args)
        for notification in repo.get_all_for_user(request.user)
    ]

    repo.remove_all_older_than(request.user, datetime.now())

    return render(request, 'notifications2/index.html', {'notifications': notifications})


from django.http import HttpResponseRedirect


def def_form(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form2 = NotificationForm(request.POST)
        # check whether it's valid:

        return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form2 = NotificationForm()

    return render(request, 'user.html', {'notificationsform': form2})

