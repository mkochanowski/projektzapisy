# -*- coding: utf-8 -*-

from django.test import TestCase
from news.models import News

import datetime

import mox

def today():
    return datetime.date(2010, 3, 26)

class NewsModelTest(TestCase):
    def test_creating_news(self):
        n1 = News(title="news test",
                  body="news body")
        self.assertEquals(str(n1), "news test")
    
class NewsManagerTest(TestCase):
    fixtures = ['news_manager_test_data.json']
    
    def test_count_new(self):
        # 4 - prawidłowa wartość z fikstury
        self.assertEquals(4, News.objects.count_new(now=today))
