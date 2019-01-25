from django.conf.urls import url
from . import views

app_name = "notifications"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^preferences/$', views.FormView, name='pref'),
]
