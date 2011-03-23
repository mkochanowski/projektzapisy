# -*- coding: utf-8 -*-
from django.contrib.syndication.feeds import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from apps.news.models import News, CATEGORIES

class LatestNews(Feed):
    base_title_prefix = ""
    base_title_suffix = ": ogłoszenia"
    description = ""
    
    def get_object(self, bits):
        if len(bits) != 1 or len(bits[0]) > 20:
            raise ObjectDoesNotExist
        return bits[0]
    
    def title(self, obj):
        return (self.base_title_prefix +
                  dict(CATEGORIES).get(obj, obj + " feed") +
                  self.base_title_suffix)
    
    def link(self, obj):
        return ("/news/" + obj + "/")

    def items(self, obj):
        return News.objects.category(obj)[:10]
    
    def item_link(self, item):
        return reverse('news-item', args=[item.id])
    
    def item_author_name(self, item):
        return item.author.get_full_name()
    
    def item_author_email(self, item):
        return item.author.email
    
    def item_pubdate(self, item):
        return item.date
