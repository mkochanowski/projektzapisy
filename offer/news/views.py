# -*- coding: utf-8 -*-

"""
    News views
"""

from django.contrib.auth.decorators import permission_required
# from django.core.urlresolvers import reverse
from django.http import HttpResponse # , Http404
from django.shortcuts import get_object_or_404, render_to_response, \
     redirect
from django.template import RequestContext
from django.utils import simplejson

from offer.news.forms import NewsForm
from offer.news.models import News
from offer.news.utils import NEWS_PER_PAGE, prepare_data, \
     render_items, get_search_results_data, mail_news_to_employees, mail_news_to_students

def main_page( request ):
    """
        Main page
    """
    return render_to_response( 'common/index.html', context_instance = RequestContext( request ) )

def ajax_latest_news(request):
    """
        Latest news
    """
    items = News.objects.new()
    data = prepare_data(request, items, quantity=len(items))
    return HttpResponse(simplejson.dumps(data))

def ajax_news_page(request, beginwith):
    """
        News page
    """
    beginwith = int(beginwith)
    items = News.objects.get_successive_news(beginwith, NEWS_PER_PAGE)
    data = prepare_data(request, items, 
                        beginwith=beginwith, quantity=NEWS_PER_PAGE,
                        archive_view=True)
    return HttpResponse(simplejson.dumps(data))

def ajax_search_page(request):
    """
        Search page
    """
    data = get_search_results_data(request)
    return HttpResponse(simplejson.dumps(data))

def search_page(request):
    """
        Search page
    """
    data = get_search_results_data(request)
    if 'message' in data: # error: bad query
        request.user.message_set.create(message=data['message'])
        return latest_news(request)
    return display_news_list(request, data)

def latest_news(request):
    """
        Latest news
    """
    items = News.objects.new()
    data = prepare_data(request, items, quantity=len(items))
    return display_news_list(request, data)

def paginated_news(request,
                   beginwith,
                   quantity=NEWS_PER_PAGE):
    """
        News page
    """
    beginwith = int(beginwith)
    items = News.objects.get_successive_news(beginwith, quantity)
    data = prepare_data(request, items,
                        beginwith=beginwith, quantity=quantity,
                        archive_view=True)
    return display_news_list(request, data)

def news_item(request, nid):
    """
        News
    """
    items = [get_object_or_404(News, pk=nid)]
    data = {}
    data['content']      = render_items(request, items)
    data['older_group']  = ""
    data['newer_group']  = ""
    data['archive_view'] = True
    return display_news_list(request, data)
    

def display_news_list(request, data={}):
    """
        NEws list
    """
    return render_to_response(
        'offer/news/list.html',
        data,
        context_instance = RequestContext(request))

@permission_required('news.add_news')
def add(request):
    """
        Add news
    """
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            request.user.message_set.create(message="Opublikowano ogłoszenie.")
            mail_news_to_employees(news)
            mail_news_to_students(news)
            return redirect(latest_news)
    else:
        form = NewsForm()
    return render_to_response('offer/news/form.html', {
        'form': form,
        'adding': True,
        },
        context_instance = RequestContext(request))

@permission_required('news.change_news')
def edit(request, nid):
    """
        Edit news
    """
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            old_news = News.objects.get(pk=nid)
            news.id = nid
            news.author = old_news.author
            news.date = old_news.date
            news.save()
            request.user.message_set.create(message="Zapisano zmiany w ogłoszeniu.")
            mail_news_to_employees(news)
            mail_news_to_students(news)
            return redirect(latest_news)
    else:
        news_instance = get_object_or_404(News, pk=nid)
        form = NewsForm(instance = news_instance)
    return render_to_response('offer/news/form.html', {
        'form': form,
        },
        context_instance = RequestContext(request))
