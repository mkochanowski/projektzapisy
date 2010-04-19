from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.enrollment.records.views',
    url('(?P<group_id>[\d]+)/assign', 'assign', name='record-assign'),
    url('(?P<group_id>[\d]+)/resign', 'resign', name='record-resign'),
    url('(?P<group_id>[\d]+)/records', 'records', name='group-records'),
    url('^schedule/prototype/$', 'schedulePrototype', name='schedule-prototype' ),
    url('^schedule/$', 'own', name='record-schedule' ),
)

