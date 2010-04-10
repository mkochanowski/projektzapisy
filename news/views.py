# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from news.models import News

news_per_page = 5

def latest_news(self):
    '''Wyświetla ogłoszenia oznaczone jako nowe.

    Jeśli nowych ogłoszeń jest więcej niż trzy,
    wyświetla wszystkie. Jeżeli nie, wyświetla
    dwa najnowsze.'''
    no_new = News.objects.count_new()
    if no_new > 2:
        return paginated_news(self,beginwith=0,
                              quantity=no_new,
                              archive=False)
    else:
        return paginated_news(self,beginwith=0,
                              quantity=2,
                              archive=False)

def paginated_news(self,
                   beginwith,
                   quantity=news_per_page,
                   archive=True):
    '''Wyświetla ogłoszenia.

    beginwith - pierwsze wyświetlane, licząc od zera
    quantity - ilość ogłoszeń na stronie'''
    beginwith = int(beginwith)
    return render_to_response(
        'news/news_list.html',
        {'object_list': News.objects.all()[beginwith:(beginwith+quantity)],
         'newer_no': beginwith,
         'newer_beginwith': max(beginwith - quantity, 0),
         'older_no': max(News.objects.count() - (beginwith + quantity), 0),
         'older_beginwith': beginwith + quantity,
         'archive_view': archive,
        },
        context_instance = RequestContext(self))
