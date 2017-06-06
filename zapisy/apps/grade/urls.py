from django.conf.urls import include, url
from . import views

# to tree/list_view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = [
    url(r'^$', views.apps.grade.poll.views.main, name='grade-main'),
    url(r'^enable_grade$', views.apps.grade.poll.views.enable_grade, name='grade-enable-grade'),
    url(r'^disable_grade$', views.apps.grade.poll.views.disable_grade, name='grade-disable-grade'),
    
    url(r'^grade_logout$', views.apps.grade.poll.views.grade_logout, name='grade-logout'),
    
    (r'^poll/', include('apps.grade.poll.urls')),
    (r'^ticket/', include('apps.grade.ticket_create.urls')),

    url(r'^declaration$', views.declaration, name='grade-poll-show'),
]
