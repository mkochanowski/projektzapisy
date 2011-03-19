from django.conf.urls.defaults import *

urlpatterns = patterns( 'apps.enrollment.records.views',
    url('(?P<group_id>[\d]+)/assign', 'assign', name='record-assign'),
    url('(?P<group_id>[\d]+)/queue_assign', 'queue_assign', name='queue-assign'),
    url('(?P<old_id>[\d]+)/change/(?P<new_id>[\d]+)/', 'change', name='record-change'),
    url('(?P<group_id>[\d]+)/resign', 'resign', name='record-resign'),
    url('(?P<group_id>[\d]+)/queue_resign', 'queue_resign', name='queue-resign'),
    url('(?P<group_id>[\d]+)/queue_inc_priority', 'queue_inc_priority', name='inc-priority'),
    url('(?P<group_id>[\d]+)/queue_dec_priority', 'queue_dec_priority', name='dec-priority'),
	url('(?P<group_id>[\d]+)/queue_set_priority/(?P<priority>[\d]+)', 'queue_set_priority', name='set-priority'),
    url('^(?P<user_id>[0-9]+)/(?P<group_id>[0-9]+)/?$', 'deleteStudentFromGroup', name='delete-student-from-group'),
    url('(?P<group_id>[\d]+)/records', 'records', name='group-records'),
    url('^schedule/prototype/pin$', 'ajaxPin', name='schedule-prototype-pin' ),
    url('^schedule/prototype/unpin$', 'ajaxUnpin', name='schedule-prototype-unpin' ),
    url('^schedule/prototype/assign$', 'ajaxAssign', name='schedule-prototype-assign' ),
    url('^schedule/prototype/resign$', 'ajaxResign', name='schedule-prototype-resign' ),
    url('^schedule/prototype/$', 'schedulePrototype', name='schedule-prototype' ),
    url('^schedule/$', 'own', name='schedule-own' ),
    url('^schedule/prototype/block$', 'blockPlan', name='schedule-prototype-block' ),
    url('^schedule/prototype/unblock$', 'unblockPlan', name='schedule-prototype-unblock' )

)

