# -*- coding: utf-8 -*-

from models import News

from datetime import datetime, timedelta
from random import randint

def generate_random_news(new=randint(1,6),
                         old=randint(1,6)):
    ns = []
    for i in xrange(new):
        n = News(title="news", body="news body",
                 date=datetime.now() - timedelta(days=randint(0,6)))
        n.save()
        ns.append(n)
    for i in xrange(old):
        n= News(title="old news", body="news body",
                date=datetime.now() - timedelta(days=randint(8,20)))
        n.save()
        ns.append(n)
    return (new, old, ns)
