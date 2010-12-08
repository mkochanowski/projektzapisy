# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

from fereol.settings import PROJECT_PATH

import os

urlpatterns = patterns('',
    #MAIN PAGE
    url('login/', login, {'template_name': 'mobile/login.html'}),
    url('^logout/$', logout, {'template_name': 'mobile/logout.html'}, name='user-mobile-logout'),
    url('^$', 'fereol.mobile.views.main_page', name='main-page'),
    url(r'^nomobile/$', 'fereol.mobile.views.noMobile', name = 'no-mobile'),
    url(r'^enrollment/$', 'fereol.mobile.views.studentSubjectList', name = 'student-enrollment'),
    url(r'^enrollment/other/', 'fereol.mobile.views.otherSubjects', name = 'enrollment-other'),
    url(r'records/schedule/$', 'fereol.mobile.views.studentSchedule', name = 'student-schedule'),
    url(r'records/schedule/(?P<schedule_owner>\d+)/(?P<delta>\-?\d+)/$', 'fereol.mobile.views.studentSchedule', name = 'student-schedule-delta'),
    url(r'^(?P<cat>[\w\-_]+)/$', 'news.views.latest_news', name='latest_news'),
    (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),
    url(r'^subject/(?P<slug>[\w\-_]+)', 'fereol.mobile.views.subjectTerms', name='subject-terms'),
    (r'^group/(?P<group_id>\d+)/assign/$', 'fereol.mobile.views.assign'),
    (r'^group/(?P<group_id>\d+)/resign/$', 'fereol.mobile.views.resign'),
    (r'^group/(?P<group_from>\d+)/(?P<group_to>\d+)/reassign/$', 'fereol.mobile.views.reassign'),
)