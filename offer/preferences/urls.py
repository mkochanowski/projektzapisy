from django.conf.urls.defaults import *

# to view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = patterns('fereol.offer.preferences.views',
    url(r'^$',       'view', name='prefs-default-view'),
    url(r'^description/(?P<proposal_id>\d+)/$', 'description', name='prefs-description'),
    url(r'^hide/(?P<pref_id>\d+)/$',  'hide',   name='prefs-hide'),
    url(r'^unhide/(?P<pref_id>\d+)/$','unhide', name='prefs-unhide'),
    url(r'^save/$', 'save_all_prefs', name='prefs-save-all'),
    url(r'^init/(?P<prop_id>\d+)/$', 'init_pref', name='prefs-init-pref'),
)
