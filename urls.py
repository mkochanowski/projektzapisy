# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

from django.contrib import admin
import os

admin.autodiscover()

from fereol.feeds import LatestNews
feeds = {
    'news': LatestNews, 
}

urlpatterns = patterns('',
    #MAIN PAGE
    url('^$', 'fereol.news.views.main_page', name='main-page'),
    #Z
    (r'^subjects/', include('fereol.enrollment.subjects.urls')),
    (r'^records/', include('fereol.enrollment.records.urls')),
    # OD
    (r'^prefs/', include('fereol.offer.preferences.urls')),
    (r'^proposal/', include('fereol.offer.proposal.urls')),
    (r'^news/', include('fereol.news.urls')),
    (r'^vote/', include('fereol.offer.vote.urls')),
    #
    (r'^jstests/', 'django.views.generic.simple.direct_to_template', {'template': 'jstests/tests.html'}),
    (r'^users/', include('fereol.users.urls')),
    (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),

    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    #CHANGE TO MOBILE
    url(r'^mobile/$', 'fereol.mobile.views.onMobile', name = 'on-mobile'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'admin/subjects/import_semester', 'fereol.enrollment.subjects.admin.views.import_semester'),
    (r'^admin/', include(admin.site.urls)),
)
