# -*- coding: utf-8 -*-
from apps.schedule.views import ClassroomTermsAjaxView

__author__ = 'maciek'


from django.conf.urls import *

urlpatterns = patterns('apps.schedule.views',
    url(r'^classrooms$', 'classrooms', name='classrooms'),
    url(r'^classrooms/terms/(?P<year>[0-9]*)/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/$', 'ajax_get_terms', name='ajax_get_terms'),
    url(r'^classrooms/reservation$', 'reservation', name='reservation'),
    url(r'^classrooms/reservations$', 'reservations', name='reservations'),
    url(r'^classrooms/(?P<slug>[0-9]+)$', 'classroom', name='classroom'),
    url(r'^classrooms/ajax/(?P<slug>[0-9]+)$', ClassroomTermsAjaxView.as_view(), name='classroom_ajax'),
    url(r'^events/(?P<id>[0-9]+)$', 'events', name='event_show'),
    url(r'^events/decision$', 'decision', name='decision'),
    url(r'^events/history$', 'history', name='history'),
    url(r'^session$', 'session', name='session'),
)