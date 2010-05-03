# -*- coding:utf-8 -*-

import datetime
from haystack import indexes
from fereol.offer.news.models import News

class NewsIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    date = indexes.DateTimeField(model_attr='date')
    def qet_queryset(self): 
        return News.objects.all()

