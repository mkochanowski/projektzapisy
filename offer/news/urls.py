from django.conf.urls.defaults import *
from django.views.generic.create_update import delete_object

from offer.news.models import News

urlpatterns = patterns('offer.news.views',
    url(r'^$', 'latest_news', name='latest_news'),
    url(r'^add/$', 'add', name='news-add'),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name='news-edit'),
    (r'^archive/from/(?P<beginwith>\d+)/$', 'paginated_news'),
    url(r'^archive/(?P<id>\d+)/$', 'news_item', name='news-item'),
    url(r'^search/$', 'search_page', name='news-search'),
    url(r'^ajax/latest/$', 'ajax_latest_news', name='news-ajax-latest'),
    url(r'^ajax/(?P<beginwith>\d+)/$', 'ajax_news_page', name='news-ajax-find'),
    url(r'^ajax/search/$', 'ajax_search_page', name='news-ajax-search'),
    url(r'^delete/(?P<object_id>\d+)/$', delete_object, {
                           'model': News,
                           'post_delete_redirect': '/news/',
                           'template_name': 'offer/news/news_confirm_delete.html',
                           'template_object_name': 'news',
                           }, name='news-delete'),
)
