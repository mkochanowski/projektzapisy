from django.conf.urls.defaults import *

# to tree/list_view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = patterns('apps.grade.poll.views',
    url(r'^$',            'default',    name='grade-default'),
    url(r'create$',       'create',     name='grade-poll-add'),
    url(r'^check_keys$',  'check_keys', name='grade-poll-verify-keys'),
)
