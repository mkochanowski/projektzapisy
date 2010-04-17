# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from news.models import News

news_per_page = 5

def latest_news(request):
    items = News.objects.new()
    data = {
        'older_no': max(News.objects.count() - len(items), 0),
        'older_beginwith': len(items),
    }
    return display_news_list(request, items, data)

def paginated_news(request,
                   beginwith,
                   quantity=news_per_page):
    beginwith = int(beginwith)
    items = News.objects.get_successive_news(beginwith, quantity)
    data = {
        'newer_no': beginwith,
        'newer_beginwith': max(beginwith - quantity, 0),
        'older_no': max(News.objects.count() - (beginwith + quantity), 0),
        'older_beginwith': beginwith + quantity,
        'archive_view': True,
    }
    return display_news_list(request, items, data)

def display_news_list(request, items, newdata={}):
    data = {
        'older_no': 0,
        'newer_no': 0,
    }
    data.update(newdata)
    data.update({ 'object_list': items, })
    return render_to_response(
        'news/news_list.html',
        data,
        context_instance = RequestContext(request))
