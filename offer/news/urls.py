from django.conf.urls.defaults import *

from offer.news.models import News

urlpatterns = patterns('offer.news.views',
    url(r'^$', 'latest_news', name='latest_news'),
    url(r'^add/$', 'add', name='news-add'),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name='news-edit'),
    (r'^archive/from/(?P<beginwith>\d+)/$', 'paginated_news'),
)
