from django.conf.urls.defaults import *

# to view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = patterns('apps.offer.preferences.views',
    url(r'^$',       'view', name='prefs-default-view'),
    url(r'^hide/$',  'hide',  {'status': True}, name='preference-hide'),
    url(r'^unhide/$',  'hide', {'status': False},  name='preference-show'),
    url(r'^save/all$', 'save_all_prefs', name='preference-save-all'),
    url(r'^save/$', 'save', name='preference-save'),
)
