from django.conf.urls.defaults import *
from django.contrib.auth.views import login

urlpatterns = patterns('fereol.users.views',
    ('login/$', login, {'template_name': 'users/login.html'}),
    ('profile/$', 'profile'),
    ('logout/$', 'logout')
)