from django.conf.urls.defaults import *

urlpatterns = patterns( 'apps.enrollment.courses.views',
    url('^(?P<slug>[\w\-_]+)$', 'course', name='course-page'),
    url('^$', 'courses',  name='course-list'),
    url('^$', 'courses',  name='enrollment-main'),
    url('^(?P<slug>[\w\-_]+)/votes$', 'votes',  name='enrollment-votes'),
    url('^(?P<slug>[\w\-_]+)/consultations$', 'course_consultations', name='course-consiltations-page'),
)
