from django.conf.urls.defaults import *

# to tree/list_view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = patterns('fereol.offer.preferences.views',
    url(r'^$',       'tree_view', name='prefs-default-view'),
    url(r'^tree/$',  'tree_view', name='prefs-tree-view'),
    url(r'^list/$',  'list_view', name='prefs-list-view'),
    url(r'^description/(?P<proposal_id>\d+)/$', 'description', name='prefs-description'),
    url(r'^hide/(?P<pref_id>\d+)/$',  'hide',   name='prefs-hide'),
    url(r'^unhide/(?P<pref_id>\d+)/$','unhide', name='prefs-unhide'),
    url(r'^set/(?P<pref_id>\d+)/$', 'set_pref', name='prefs-set-pref'),
    url(r'^init/(?P<prop_id>\d+)/$', 'init_pref', name='prefs-init-pref'),
)
