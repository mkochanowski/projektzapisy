from django.conf.urls import url, include
from rest_framework import routers

from rest_api import test as test_rest_api
from . import views

router = routers.DefaultRouter()
router.register(r'test', test_rest_api.UserViewSet)
# router.register(r'semester', semester_api.get_semester_list)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url('^(?P<slug>[\w\-_]+)$', views.course, name='course-page'),
    url('^$', views.courses, name='course-list'),
    url('^$', views.courses, name='enrollment-main'),
    url('^get_semester_info/(?P<semester_id>\d+)$', views.get_semester_info),
]
