from haystack.sites import site
from fereol.offer.news.models import News
from fereol.offer.news.search_indexes import NewsIndex

site.register(News, NewsIndex)

