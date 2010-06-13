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

from news.forms import NewsForm
from news.models import News
from news.utils import NEWS_PER_PAGE, prepare_data, render_items, \
     get_search_results_data, mail_news_to_employees, \
     mail_news_to_students, render_with_category_template

def main_page( request ):
    """
        Main page
    """
    return render_to_response( 'common/index.html', context_instance = RequestContext( request ) )

def search_page(request, cat):
    """
        Search page
    """
    json = request.GET.get('json', None)
    data = get_search_results_data(request, cat)
    if json:
        return HttpResponse(simplejson.dumps(data))
    if 'message' in data: # error: bad query
        request.user.message_set.create(message=data['message'])
        return latest_news(request)
    return display_news_list(request, data)

def latest_news(request, cat):
    """
        Latest news
    """
    json = request.GET.get('json', None)
    items = News.objects.new(cat)
    data = prepare_data(request, items, quantity=len(items), category=cat)
    if json:
        return HttpResponse(simplejson.dumps(data))
    return display_news_list(request, data)

def paginated_news(request, cat,
                   beginwith,
                   quantity=NEWS_PER_PAGE):
    """
        News page
    """
    json = request.GET.get('json', None)
    beginwith = int(beginwith)
    items = News.objects.get_successive_news(cat, beginwith, quantity)
    data = prepare_data(request, items,
                        beginwith=beginwith, quantity=quantity,
                        archive_view=True, category=cat)
    if json:
        return HttpResponse(simplejson.dumps(data))
    return display_news_list(request, data)

def news_item(request, nid):
    """
        News
    """
    items = [get_object_or_404(News, pk=nid)]
    data = {}
    data['category']     = items[0].category
    data['content']      = render_items(request, items)
    data['older_group']  = ""
    data['newer_group']  = ""
    data['archive_view'] = True
    return display_news_list(request, data)
    

def display_news_list(request, data={}):
    """
        NEws list
    """
    return render_with_category_template(
        'news/list.html',
        RequestContext(request,data))

@permission_required('news.add_news')
def add(request, cat):
    """
        Add news
    """
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.category    = cat
            news.save()
            request.user.message_set.create(message="Opublikowano ogłoszenie.")
            mail_news_to_employees(news)
            mail_news_to_students(news)
            return redirect(latest_news, cat)
    else:
        form = NewsForm()
    return render_with_category_template('news/form.html',
        RequestContext(request, {
        'category': cat,
        'form': form,
        'adding': True,
        }))

@permission_required('news.change_news')
def edit(request, cat, nid):
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
            news.category  = old_news.category
            news.save()
            request.user.message_set.create(message="Zapisano zmiany w ogłoszeniu.")
            mail_news_to_employees(news)
            mail_news_to_students(news)
            return redirect(latest_news, news.category)
    else:
        news_instance = get_object_or_404(News, pk=nid)
        form = NewsForm(instance = news_instance)
    return render_with_category_template('news/form.html',
        RequestContext({
        'category': cat,
        'form': form,
        }))
