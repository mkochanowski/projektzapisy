# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.offer.desiderata.views',
    url(r'/change$', 'change_desiderata', name='change_desiderata'),
)