from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.enrollment.subjects.views',
    url('^ajax-list$', 'list_of_subjects',  name='subject-ajax'),
    url('(?P<slug>[\w\-_]+)', 'subject', name='subject-page'),
    url('^$', 'subjects',  name='subject-list'),
)
