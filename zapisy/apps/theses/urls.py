from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.theses_main, name='main'),
]
