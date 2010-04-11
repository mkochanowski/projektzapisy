from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.records.views',
    url('(?P<group_id>[\d]+)/assign', 'assign', name='record-assign'),
    url('(?P<group_id>[\d]+)/resign', 'resign', name='record-resign'),
    url('^schedule/prototype/$', 'schedulePrototype', name='schedule-prototype' ),
    url('^schedule/$', 'own', name='record-schedule' ),
    url('^offer/$', 'didacticOffer', name='didactic-offer' ),
)

