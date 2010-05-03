# -*- coding: utf-8 -*-

from django.template import Context, RequestContext
from django.template.loader import get_template

from news.models import News

news_per_page = 5

def render_items(request, items):
    c = RequestContext(request, {
        'object_list':items,
    } )
    t = get_template('offer/news/news_ajax_list.html')
    return t.render(c)

def render_newer_group(beginwith, quantity):
    c = Context( {
        'newer_no':quantity,
        'newer_beginwith':beginwith,
    } )
    t = get_template('offer/news/news_newer_group.html')
    return t.render(c)

def render_older_group(beginwith, quantity):
    c = Context( {
        'older_no':quantity,
        'older_beginwith':beginwith,
    } )
    t = get_template('offer/news/news_older_group.html')
    return t.render(c)

def prepare_data(request, items,
                 beginwith=0, quantity=news_per_page,
                 archive_view=False):
    news_count = News.objects.count()
    data = {}
    data['content']     = render_items(request, items)
    data['older_group'] = render_older_group(
        beginwith + quantity, 
        max(news_count-(beginwith+quantity),0))
    data['newer_group'] = render_newer_group(
        max(beginwith - quantity, 0),
        beginwith)
    data['archive_view'] = archive_view
    return data
