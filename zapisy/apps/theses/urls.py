from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('theses', views.ThesesViewSet, base_name="theses_list")

urlpatterns = [
    url(r'^$', views.theses_main, name='main'),
    url(r'^api/', include(router.urls))
]
