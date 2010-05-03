# -*- coding: utf-8 -*-

from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.template import Context, RequestContext
from django.template.loader import get_template
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

from fereol.offer.news.models import News

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
    data['search_view']  = False
    return data

def render_search_newer_group(page, query):
    c = Context( {
        'page':  page,
        'query': query,
    } )
    t = get_template('offer/news/news_search_newer_group.html')
    return t.render(c)

def render_search_older_group(page, query):
    c = Context( {
        'page':  page,
        'query': query,
    } )
    t = get_template('offer/news/news_search_older_group.html')
    return t.render(c)

def get_search_results_data(request):
    try:
        page_n = request.GET.get('page', 1)
        sqs  = SearchQuerySet().order_by('-date')
        form = SearchForm(request.GET, searchqueryset=sqs,
                          load_all=False)
        if 'q' in request.GET and request.GET['q'] and form.is_valid():
            query = form.cleaned_data['q']
            results = map(lambda r: r.object, form.search())
            paginator = Paginator(results, news_per_page)
            page = paginator.page(page_n)
            data = {}
            data['content'] = render_items(request, page.object_list)
            data['newer_group']  = render_search_newer_group(page, query)
            data['older_group']  = render_search_older_group(page, query)
            data['archive_view'] = False
            data['search_view']  = True
            return data
        else:
            msg = "Niewłaściwe zapytanie"
            data = {'message': msg}
            return data
    except InvalidPage:
        raise Http404
