#-*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns( 'apps.enrollment.records.views',
	url('^(?P<group_id>[\d]+)/queue_set_priority(?P<method>\.json)?$', 'queue_set_priority', name='set-priority'),
    url('^(?P<group_id>[\d]+)/records$', 'records', name='group-records'),
    url('^schedule/prototype/set-pinned$', 'prototype_set_pinned', name='schedule-prototype-set-pinned' ),
    url('^set-enrolled(?P<method>\.json)?$', 'set_enrolled', name='schedule-set-enrolled' ),
    url('^schedule/prototype/$', 'schedule_prototype', name='schedule-prototype' ),
    url('^schedule/$', 'own', name='schedule-own' ),
    url('^schedule/prototype/block$', 'blockPlan', name='schedule-prototype-block' ), #TODO: scalić w jedno
    url('^schedule/prototype/unblock$', 'unblockPlan', name='schedule-prototype-unblock' ) #TODO: scalić w jedno
)
