from django.conf.urls.defaults import *

urlpatterns = patterns( 'apps.enrollment.courses.views',
    url('^(?P<slug>[\w\-_]+)$', 'course', name='course-page'),
    url('^$', 'courses',  name='course-list'),
)
