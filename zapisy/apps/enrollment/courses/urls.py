from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url('^(?P<slug>[\w\-_]+)$', views.course, name='course-page'),
    url('^$', views.courses, name='course-list'),
    url('^$', views.courses, name='enrollment-main'),
    url('^get_semester_info/(?P<semester_id>\d+)$', views.get_semester_info),
]
