from django.conf.urls.defaults import *
from django.views.generic.create_update import delete_object

from news.models import News

urlpatterns = patterns('news.views',
    url(r'^(?P<cat>[\w\-_]+)/$', 'latest_news', name='latest_news'),
    url(r'^(?P<cat>[\w\-_]+)/add/$', 'add', name='news-add'),
    url(r'^(?P<cat>[\w\-_]+)/edit/(?P<nid>\d+)/$', 'edit', name='news-edit'),
    url(r'^(?P<cat>[\w\-_]+)/archive/from/(?P<beginwith>\d+)/$', 'paginated_news', name='news-page'),
    url(r'^archive/(?P<nid>\d+)/$', 'news_item', name='news-item'),
    url(r'^(?P<cat>[\w\-_]+)/search/$', 'search_page', name='news-search'),
    url(r'^delete/(?P<object_id>\d+)/$', delete_object, {
                           'model': News,
                           'post_delete_redirect': '/news/',
                           'template_name': 'news/confirm_delete.html',
                           'template_object_name': 'news',
                           }, name='news-delete'),
)
