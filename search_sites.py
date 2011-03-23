from haystack.sites import site
from apps.news.models import News
from apps.news.search_indexes import NewsIndex

site.register(News, NewsIndex)

