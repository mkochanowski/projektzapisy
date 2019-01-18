from django.conf.urls import url
from . import views

app_name = "notifications2"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pref/$', views.FormView, name='pref'),
]
