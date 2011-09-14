from django.conf.urls.defaults import *

from apps.news.models import News

urlpatterns = patterns('apps.news.views',
    url(r'^$','all_news',name='news-all'),
    url(r'^add/$', 'all_news_add', name='news-all-add'),
    url(r'^delete/(?P<nid>\d+)/$', 'all_news_delete', name='news-all-delete'),
    url(r'^edit/(?P<nid>\d+)/$', 'all_news_edit', name='news-all-edit'),
    url(r'^search/$', 'search_page', name='news-search'),
    # STARA WERSJA
    #url(r'^(?P<cat>[\w\-_]+)/$', 'latest_news', name='latest_news'),
    #url(r'^(?P<cat>[\w\-_]+)/add/$', 'add', name='news-add'),
    #url(r'^(?P<cat>[\w\-_]+)/edit/(?P<nid>\d+)/$', 'edit', name='news-edit'),
    #url(r'^(?P<cat>[\w\-_]+)/archive/from/(?P<beginwith>\d+)/$', 'paginated_news', name='news-page'),
    #url(r'^archive/(?P<nid>\d+)/$', 'news_item', name='news-item'),
    #url(r'^(?P<cat>[\w\-_]+)/search/$', 'search_page', name='news-search'),
    #url(r'^delete/(?P<nid>\d+)/$', 'delete', name='news-delete'),
)
