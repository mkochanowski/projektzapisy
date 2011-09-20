# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from apps.news.models import News
from django.contrib.syndication.views import Feed

class LatestNews(Feed):
    base_title_prefix = ""
    base_title_suffix = ": ogłoszenia"
    description = ""

    
    def link(self):
        return ("/news/")

    def items(self):
        return News.objects.exclude(category='-').select_related('author')[:10]
    
    def item_link(self, item):
        return ("/news/")
    
    def item_author_name(self, item):
        return item.author.get_full_name()
    
    def item_author_email(self, item):
        return item.author.email
    
    def item_pubdate(self, item):
        return item.date
