from django.conf.urls.defaults import *
from django.contrib.auth.views import login

urlpatterns = patterns('fereol.users.views',
    url('login/$', login, {'template_name': 'users/login.html'}, 'user-login'),
    ('profile/$', 'profile'),
    url('logout/$', 'logout', name='user-logout'),
)
