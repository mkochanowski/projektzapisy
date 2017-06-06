from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns( 'apps.enrollment.courses.views',
    url('^(?P<slug>[\w\-_]+)$', views.course, name='course-page'),
    url('^$', views.courses,  name='course-list'),
    url('^$', views.courses,  name='enrollment-main'),
    url('^(?P<slug>[\w\-_]+)/votes$', views.votes,  name='course-votes'),
    url('^(?P<slug>[\w\-_]+)/consultations$', views.course_consultations, name='course-consiltations-page'),
    url('^get_semester_info/(?P<semester_id>\d+)$', views.get_semester_info),
)
