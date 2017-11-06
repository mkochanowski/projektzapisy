# -*- coding: utf-8 -*-
import django.conf.urls as urls

from apps.users.api import StudentList

urlpatterns = urls.patterns('', urls.url('^student/$', StudentList.as_view()))
