from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$',              'fereol.grade.poll.views.default',                name='grade-default'),
   
    url(r'^prepare_grade$', 'fereol.grade.ticket_create.views.prepare_grade', name='grade-prepare-grade'),
    url(r'^enable_grade$',  'fereol.grade.poll.views.enable_grade',           name='grade-enable-grade'),
    url(r'^disable_grade$', 'fereol.grade.poll.views.disable_grade',          name='grade-disable-grade'),
    
    (r'^poll/',   include('fereol.grade.poll.urls')),
    (r'^ticket/', include('fereol.grade.ticket_create.urls')),
)
