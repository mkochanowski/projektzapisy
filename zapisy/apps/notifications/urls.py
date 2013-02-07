# -*- coding: utf-8 -*-

__author__ = 'maciek'


from django.conf.urls import *

urlpatterns = patterns('apps.notifications.views',
    url(r'^notifications/save$', 'save', name='save'),
)