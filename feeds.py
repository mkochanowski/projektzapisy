# -*- coding: utf-8 -*-
from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from offer.news.models import News

class LatestNews(Feed):
    title = "Zapisy: ogłoszenia"
    link  = "/news/"
    description = ""
    
    def items(self):
        return News.objects.all()[:10]
    
    def item_link(self, item):
        return reverse('news-item', args=[item.id])
