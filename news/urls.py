from django.conf.urls.defaults import *

from news.models import News

urlpatterns = patterns('news.views',
    (r'^$', 'latest_news'),
    (r'^archive/from/(?P<beginwith>\d+)/$', 'paginated_news'),
)
