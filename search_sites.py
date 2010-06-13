from haystack.sites import site
from fereol.news.models import News
from fereol.news.search_indexes import NewsIndex

site.register(News, NewsIndex)

