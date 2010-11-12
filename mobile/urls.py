from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #MAIN PAGE
    url('^$', 'fereol.mobile.views.main_page', name='main-page'),
    url(r'^nomobile/$', 'fereol.mobile.views.noMobile', name = 'no-mobile'),
    url(r'^(?P<cat>[\w\-_]+)/$', 'news.views.latest_news', name='latest_news'),
)
