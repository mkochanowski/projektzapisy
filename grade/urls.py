from django.conf.urls.defaults import *

# to tree/list_view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = patterns('fereol.grade.poll.views',
    url(r'^$',       'create', name='grade-default-view'),
)
