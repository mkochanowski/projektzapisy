# -*- coding: utf-8 -*-

import django_filters
from apps.schedule.models import Event, Term


class EventFilter(django_filters.FilterSet):
    class Meta:
        model = Event
        fields = ['title', 'type', 'visible', 'status']


class ExamFilter(django_filters.FilterSet):
    class Meta:
        model = Term
        fields = ['event__course__semester']