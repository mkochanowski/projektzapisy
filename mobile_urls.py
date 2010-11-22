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
	url(r'^enrollment/(?P<slug>[\w\-_]+)/$', 'abc', name = 'enrollment-subject'),
	url(r'records/schedule/$', 'fereol.mobile.views.studentPlan', name = 'student-plan'),
	url(r'records/schedule/(?P<delta>\-?\d+)/$', 'fereol.mobile.views.studentPlan', name = 'student-plan-delta'),
    url(r'^(?P<cat>[\w\-_]+)/$', 'news.views.latest_news', name='latest_news'),
	(r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),
)
