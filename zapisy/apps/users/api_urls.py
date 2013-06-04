# -*- coding: utf-8 -*-
from django.conf.urls import *
from apps.users.api import StudentList

urlpatterns = patterns('',
                       url('^student/$', StudentList.as_view())
)
