# -*- coding: utf-8 -*-

from django.test import TestCase

from utils import generate_random_news

from news.templatetags.news_extras import *

class NewsTagsTest(TestCase):
    def test_newscount(self):
        (new, old, ns) = generate_random_news()
        self.assertEquals(str(new), newscount())
        for n in News.objects.all():
            n.delete()
        self.assertEquals("0", newscount())
