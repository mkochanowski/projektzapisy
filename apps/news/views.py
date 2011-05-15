# -*- coding: utf-8 -*-

"""
    News views
"""

from django.contrib.auth.decorators import permission_required
# from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect # , Http404
from django.shortcuts import get_object_or_404, render_to_response, \
     redirect
from django.template import RequestContext
from django.utils import simplejson
from django.views.generic.create_update import delete_object

from apps.news.forms import NewsForm
from apps.news.models import News
from apps.news.utils import NEWS_PER_PAGE, prepare_data, render_items, \
     get_search_results_data, mail_news_enrollment,  mail_news_grade, \
     mail_news_offer, render_with_category_template, render_with_device_detection
from apps.enrollment.courses.models import Semester

def main_page( request ):
    """
        Main page
    """
    try:
        grade = Semester.get_current_semester().is_grade_active
    except:
        grade = False
    return render_to_response('common/index.html', {'grade':grade}, context_instance = RequestContext(request))


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
    try:
        grade = Semester.get_current_semester().is_grade_active
    except:
        grade = False
    data['grade'] = grade
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
            if cat == 'offer':
                mail_news_offer(news)
            elif cat == 'enrollment':
                mail_news_enrollment(news)
            elif cat == 'grade':
                mail_news_grade(news)
            return redirect(latest_news, cat)
    else:
        form = NewsForm()
    try:
        grade = Semester.get_current_semester().is_grade_active
    except:
        grade = False
    return render_with_category_template('news/form.html',
        RequestContext(request, {
        'category': cat,
        'form': form,
        'adding': True,
        'grade' : grade
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
            if cat == 'offer':
                mail_news_offer(news)
            elif cat == 'enrollment':
                mail_news_enrollment(news)
            elif cat == 'grade':
                mail_news_grade(news)
            return redirect(latest_news, news.category)
    else:
        news_instance = get_object_or_404(News, pk=nid)
        form = NewsForm(instance = news_instance)
    return render_with_category_template('news/form.html',
        RequestContext(request, {
        'category': cat,
        'form': form,
        'grade' : Semester.get_current_semester().is_grade_active
        }))

@permission_required('news.delete_news')
def delete(request, nid):
    """ Delete news item"""
    news = get_object_or_404(News, pk=nid)
    category = news.category
    if request.method == 'POST':
        news.delete()
        request.user.message_set.create(message="Usunięto ogłoszenie.")
        return redirect(latest_news, category)
    try:
        grade = Semester.get_current_semester().is_grade_active
    except:
        grade = False
    return render_with_category_template('news/confirm_delete.html',
        RequestContext(request, {
            'category': category,
            'news': news,
            'grade' : grade
        }))
