# -*- coding: utf-8 -*-

import django_filters
from apps.schedule.models import Event


class EventFilter(django_filters.FilterSet):
    class Meta:
        model = Event
        fields = ['title', 'type', 'visible', 'status']


