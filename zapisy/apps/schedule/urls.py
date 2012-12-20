# -*- coding: utf-8 -*-
__author__ = 'maciek'


from django.conf.urls import *

urlpatterns = patterns('apps.schedule.views',
    url(r'^classrooms$', 'classrooms', name='list'),
    url(r'^classrooms/terms/(?P<year>[0-9]*)/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/$', 'ajax_get_terms', name='ajax_get_terms'),
    url(r'^classrooms/reservation$', 'reservation', name='reservation'),
    url(r'^classrooms/reservations$', 'reservations', name='reservations'),
    url(r'^classrooms/(?P<slug>[\w\-_]+)$', 'classroom', name='show'),
    url(r'^events/(?P<id>[0-9]+)$', 'events', name='event_show'),
    url(r'^events/decision$', 'decision', name='decision'),
    url(r'^events/history', 'history', name='history'),
)