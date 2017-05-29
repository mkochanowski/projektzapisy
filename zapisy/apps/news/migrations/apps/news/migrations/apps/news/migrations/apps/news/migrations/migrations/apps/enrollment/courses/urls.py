from django.conf.urls import patterns, url

urlpatterns = patterns( 'apps.enrollment.courses.views',
    url('^(?P<slug>[\w\-_]+)$', 'course', name='course-page'),
    url('^$', 'courses',  name='course-list'),
    url('^$', 'courses',  name='enrollment-main'),
    url('^(?P<slug>[\w\-_]+)/votes$', 'votes',  name='course-votes'),
    url('^(?P<slug>[\w\-_]+)/consultations$', 'course_consultations', name='course-consiltations-page'),
)
