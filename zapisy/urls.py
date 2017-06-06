# -*- coding: utf-8 -*-

import os
import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from feeds import LatestNews
from apps.news import views as news_views

admin.autodiscover()



urlpatterns = [
    url('^$', news_views.main_page, name='main-page'),
    url(r'^help/', include('apps.help.urls')),
    url(r'^courses/', include('apps.enrollment.courses.urls')),
    url(r'^records/', include('apps.enrollment.records.urls')),
    url(r'^statistics/', include('apps.statistics.urls', namespace='statistics')),
    url(r'^consultations/$', 'apps.users.views.consultations_list', name="consultations-list"),

    url(r'^news/', include('apps.news.urls')),
    url(r'^jstests/', TemplateView.as_view(template_name="jstests/tests.html")),
    url(r'^users/', include('apps.users.urls')),
    url('accounts/', include('apps.email_change.urls')),

    url(r'^grade/', include('apps.grade.urls')),
    url(r'^feeds/news/$', LatestNews()),
    url(r'^s/(?P<query>.*)/$', 'apps.users.views.students_list', name='users-list-search'),
    url(r'^e/(?P<query>.*)/$', 'apps.users.views.employees_list', name='users-list-search'),

    url(r'^fereol_admin/courses/import_semester', 'apps.enrollment.courses.admin.views.import_semester'),
    url(r'^fereol_admin/courses/import_schedule', 'apps.enrollment.courses.admin.views.import_schedule'),
    url(r'^fereol_admin/courses/refresh_semester', 'apps.enrollment.courses.admin.views.refresh_semester'),
    url(r'^fereol_admin/courses/group/change_limit', 'apps.enrollment.courses.admin.views.change_group_limit', name='change-group-limit'),
    url(r'^fereol_admin/courses/group/remove_student', 'apps.enrollment.courses.admin.views.remove_student'),
    url(r'^fereol_admin/courses/group/add_student', 'apps.enrollment.courses.admin.views.add_student'),
    url(r'^offer', include('apps.offer.proposal.urls')),
    url(r'^prefs/', include('apps.offer.preferences.urls')),
    url(r'^desiderata', include('apps.offer.desiderata.urls')),
    url(r'^', include('apps.schedule.urls', namespace='events')),
    url(r'^', include('apps.notifications.urls', namespace='notifications')),
    url(r'^vote/', include('apps.offer.vote.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^fereol_admin/', include(admin.site.urls)),

)


if not settings.RELEASE:
    urlpatterns += patterns('',
    url(r'^static/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
    url(r'^vote/', include('apps.offer.vote.urls')),
    # OD
    #url('^offer/$', 'apps.offer.proposal.views.main', name='offer-main'),
    # OCENA ZAJĘĆ

    url(r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')})

    #

    #CHANGE TO apps.mobile
    #url(r'^mobile/$', 'apps.mobile.views.onMobile', name = 'on-mobile'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


)
