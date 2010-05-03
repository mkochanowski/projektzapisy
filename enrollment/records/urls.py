from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.enrollment.records.views',
    url('(?P<group_id>[\d]+)/assign', 'assign', name='record-assign'),
    url('(?P<old_id>[\d]+)/change/(?P<new_id>[\d]+)/', 'change', name='record-change'),
    url('(?P<group_id>[\d]+)/resign', 'resign', name='record-resign'),
    url('(?P<group_id>[\d]+)/records', 'records', name='group-records'),
    url('^schedule/prototype/pin$', 'ajaxPin', name='schedule-prototype-pin' ),
    url('^schedule/prototype/unpin$', 'ajaxUnpin', name='schedule-prototype-unpin' ),
    url('^schedule/prototype/assign$', 'ajaxAssign', name='schedule-prototype-assign' ),
    url('^schedule/prototype/resign$', 'ajaxResign', name='schedule-prototype-resign' ),
    url('^schedule/prototype/$', 'schedulePrototype', name='schedule-prototype' ),
    url('^schedule/$', 'own', name='schedule-own' ),
)

