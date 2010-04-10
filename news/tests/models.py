# -*- coding: utf-8 -*-

from django.test import TestCase
from news.models import News

from utils import generate_random_news

class NewsModelTest(TestCase):
    def test_creating_news(self):
        n1 = News(title="news test",
                  body="news body")
        self.assertEquals(str(n1), "news test")
    
class NewsManagerTest(TestCase):
    def test_count_new(self):
        (new, old, ns) = generate_random_news()
        self.assertEquals(new, News.objects.count_new())
        for n in ns:
            n.delete()
    
