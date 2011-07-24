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
    url('^$', 'apps.news.views.main_page', name='main-page'),
    #HELP
    (r'^help/', include('apps.help.urls')),
    #Z
    url('^enrollment/$', 'apps.enrollment.courses.views.main', name='enrollment-main'),
    (r'^courses/', include('apps.enrollment.courses.urls')),
    (r'^records/', include('apps.enrollment.records.urls')),
    # OD
    url('^offer/$', 'apps.offer.proposal.views.main', name='offer-main'),
    (r'^prefs/', include('apps.offer.preferences.urls')),
    (r'^proposal/', include('apps.offer.proposal.urls')),
    (r'^news/', include('apps.news.urls')),
    (r'^vote/', include('apps.offer.vote.urls')),
    # OCENA ZAJĘĆ
    (r'^grade/', include('apps.grade.urls')),
    #
    (r'^jstests/', 'django.views.generic.simple.direct_to_template', {'template': 'jstests/tests.html'}),
    (r'^users/', include('apps.users.urls')),
    ('accounts/', include('apps.email_change.urls')),
    (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),

    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    #CHANGE TO apps.mobile
    #url(r'^mobile/$', 'apps.mobile.views.onMobile', name = 'on-mobile'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^fereol_admin/courses/import_semester', 'apps.enrollment.courses.admin.views.import_semester'),
    (r'^fereol_admin/', include(admin.site.urls)),
)
