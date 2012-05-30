#-*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('apps.enrollment.records.views',
    # records
    url('^set-enrolled(?P<method>\.json)?$',\
        'set_enrolled', name='records-set-enrolled'),
    url('^set-queue-priority(?P<method>\.json)?$',\
        'set_queue_priority', name='records-set-queue-priority'),
    url('^(?P<group_id>[\d]+)/records$',\
        'records', name='records-group'),
    url('^(?P<group_id>[\d]+)/records/csv$',\
        'records_csv', name='records-csv'),
    url('^set-locked(?P<method>\.json)?$',\
        'records_set_locked', name='records-set-locked' ),

    #schedule and schedule prototype
    url('^schedule/$',\
        'own', name='schedule-own' ),
    url('^schedule/prototype/$',\
        'schedule_prototype', name='schedule-prototype' ),
    url('^schedule/prototype/set-pinned$',\
        'prototype_set_pinned', name='schedule-prototype-set-pinned' ),
)
