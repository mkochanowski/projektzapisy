# -*- coding:utf-8 -*-

"""
    Indexes for search
"""

# import datetime
from haystack import indexes
from offer.news.models import News

class NewsIndex(indexes.RealTimeSearchIndex):
    """
        Creates index
    """
    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateTimeField(model_attr='date')
    def qet_queryset(self):
        """
            Gets all news
        """ 
        return News.objects.all()

