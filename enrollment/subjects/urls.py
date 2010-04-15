from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.enrollment.subjects.views',
    url('(?P<slug>[\w\-_]+)', 'subject', name='subject-page'),
    url('^$', 'subjects',  name='subject-list'),
)
