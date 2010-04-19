# -*- coding: utf-8 -*-

from django.test import TestCase
from offer.news.models import News

from utils import generate_random_news

from datetime import datetime, timedelta
from random import randint

class NewsModelTest(TestCase):
    def test_creating_news(self):
        n1 = News(title="news test",
                  body="news body")
        self.assertEquals(str(n1), "news test")
    
class NewsManagerTest(TestCase):
    def test_new(self):
        (new, old, ns) = generate_random_news()
        def f(o): return o.id
        nss = map(f, News.objects.new())
        ncs = map(f, sorted(ns,
                key=(lambda o:o.date), reverse=True)[0:max(new,3)])
        self.assertEquals(nss, ncs)
        for n in ns:
            n.delete()
    def test_count_new(self):
        self.assertEquals(0, News.objects.count_new())
        (new, old, ns) = generate_random_news()
        self.assertEquals(new, News.objects.count_new())
        for n in ns:
            n.delete()
    def test_get_successive_news(self):
        ns = []
        for i in xrange(12):
            n = News(title="news", body="news body", author_id=1,
                     date=datetime.now() - timedelta(days=12-i))
            n.save()
            ns.append(n)
        self.assertEquals(0, len(News.objects.get_successive_news(0,0)))
        self.assertEquals(0,len(
            News.objects.get_successive_news(randint(0,11),0)))
        self.assertEquals(12, len(
            News.objects.get_successive_news(0,20)))
        nss = News.objects.get_successive_news(3, 6)
        for i in xrange(0, 6):
            self.assertEquals(nss[i].id, ns[8-i].id)
        for n in ns:
            n.delete()
    
