# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from apps.notifications.forms import NotificationFormset

__author__ = 'maciek'


@require_POST
@login_required
def save(request):

    formset = NotificationFormset(request.POST)

    if formset.is_valid():
        formset.save()
        messages.success(request, u'Zmieniono ustawienia powiadomień')

    else:
        messages.error(request, u'Wystąpił błąd przy zapisie zmian ustawień')

    return redirect('my-profile')