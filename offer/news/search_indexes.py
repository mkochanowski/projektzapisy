# -*- coding:utf-8 -*-

import datetime
from haystack import indexes
from offer.news.models import News

class NewsIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateTimeField(model_attr='date')
    def qet_queryset(self): 
        return News.objects.all()

