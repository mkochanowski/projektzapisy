# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from offer.news.models import News
from offer.news.forms import NewsForm

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
        'offer/news/news_list.html',
        data,
        context_instance = RequestContext(request))

@permission_required('news.add_news')
def add(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            request.user.message_set.create(message="Opublikowano ogłoszenie.")
            return redirect(latest_news)
    else:
        form = NewsForm()
    return render_to_response('offer/news/news_form.html', {
        'form': form,
        'adding': True,
        },
        context_instance = RequestContext(request))

@permission_required('news.change_news')
def edit(request, id):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            old_news = News.objects.get(pk=id)
            news.id = id
            news.author = old_news.author
            news.date = old_news.date
            news.save()
            request.user.message_set.create(message="Zapisano zmiany w ogłoszeniu.")
            return redirect(latest_news)
    else:
        news_instance = get_object_or_404(News, pk=id)
        form = NewsForm(instance = news_instance)
    return render_to_response('offer/news/news_form.html', {
        'form': form,
        },
        context_instance = RequestContext(request))
