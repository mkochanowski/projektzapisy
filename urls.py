from django.conf.urls.defaults import *

from django.contrib import admin
import os

admin.autodiscover()

urlpatterns = patterns('',
    (r'^users/', include('fereol.users.urls')),
    (r'^subjects/', include('fereol.subjects.urls')),
    (r'^records/', include('fereol.records.urls')),
    (r'^news/', include('fereol.news.urls')),
    (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
)
