# -*- coding: utf-8 -*-

"""
    News views
"""

from django.contrib.auth.decorators import permission_required
# from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect # , Http404
from django.shortcuts import get_object_or_404, render_to_response, \
     redirect
from django.template import RequestContext
from django.utils import simplejson
from django.views.generic.create_update import delete_object

from apps.news.forms import NewsForm, NewsAllForm
from apps.news.models import News
from apps.news.utils import NEWS_PER_PAGE, prepare_data, prepare_data_all, render_items, \
     get_search_results_data, mail_news_enrollment,  mail_news_grade, \
     mail_news_offer, render_with_category_template, render_with_device_detection
from apps.enrollment.courses.models import Semester
from apps.users.models import BaseUser
from django.template.loader import get_template
import datetime

def main_page( request ):
    """
        Main page
    """
    try:
        news = News.objects.all()[0]
    except ObjectDoesNotExist:
        news = None

    return render_to_response('common/index.html', {'news': news}, context_instance = RequestContext(request))


def search_page(request):
    """
        Search page
    """
    json = request.GET.get('json', None)
    data = get_search_results_data(request, None)
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
        'grade' : grade,
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
        'grade' : Semester.get_current_semester().is_grade_active,
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
            'grade' : grade,
        }))

# NOWA WERSJA AKTUALNOŚCI ZE ZMERGOWANYMI SYSTEMAMI PONIZEJ

def all_news(request):
    """
        Latest news
    """
    try:
        student = request.user.student
        student.last_news_view = datetime.datetime.now()
        student.save()
    except:
        try:
            employee = request.user.employee
            employee.last_news_view = datetime.datetime.now()
            employee.save()   
        except:
            pass
    
    json = request.GET.get('json', None)
    items = News.objects.all()
    data = prepare_data_all(request, items)
    if json:
        return HttpResponse(simplejson.dumps(data))

    try:
        grade = Semester.get_current_semester().is_grade_active
    except:
        grade = False
    data['grade'] = grade

    temp = get_template('news/list_all.html')
    return HttpResponse(temp.render(RequestContext(request,data)))

@permission_required('news.add_news')
def all_news_add(request):
    """
        Add news
    """
    if request.method == 'POST':
        form = NewsAllForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            request.user.message_set.create(message="Opublikowano ogłoszenie.")
            """if cat == 'offer':
                mail_news_offer(news)
            elif cat == 'enrollment':
                mail_news_enrollment(news)
            elif cat == 'grade':
                mail_news_grade(news)"""
            return redirect(all_news)
    else:
        form = NewsAllForm()
    try:
        grade = Semester.get_current_semester().is_grade_active
    except:
        grade = False
    """return render_with_category_template('news/form_all.html',
        RequestContext(request, {
        'form': form,
        'adding': True,
        'grade' : grade,
        }))"""
    data = {
        'form': form,
        'adding': True,
        'grade' : grade,
        }
    temp = get_template('news/form_all.html')
    return HttpResponse(temp.render(RequestContext(request,data)))
        
@permission_required('news.delete_news')
def all_news_delete(request, nid):
    """ Delete news item"""
    news = get_object_or_404(News, pk=nid)
    category = news.category
    if request.method == 'POST':
        news.delete()
        request.user.message_set.create(message="Usunięto ogłoszenie.")
        return redirect(all_news)
    try:
        grade = Semester.get_current_semester().is_grade_active
    except:
        grade = False
    data = {
            'news': news,
            'grade' : grade,
        }
    temp = get_template('news/confirm_delete_all.html')
    return HttpResponse(temp.render(RequestContext(request,data)))
    
        
@permission_required('news.change_news')
def all_news_edit(request, nid):
    """
        Edit news
    """
    if request.method == 'POST':
        form = NewsAllForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            old_news = News.objects.get(pk=nid)
            news.id = nid
            news.author = old_news.author
            news.date = old_news.date
            news.category  = old_news.category
            news.save()
            request.user.message_set.create(message="Zapisano zmiany w ogłoszeniu.")
            return redirect(all_news)
    else:
        news_instance = get_object_or_404(News, pk=nid)
        form = NewsAllForm(instance = news_instance)
    try:
        grade = Semester.get_current_semester().is_grade_active
    except:
        grade = False        
    data = {
        'form': form,
        'grade' : grade,
        }
    temp = get_template('news/form_all.html')
    return HttpResponse(temp.render(RequestContext(request,data)))
