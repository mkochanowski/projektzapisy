# -*- coding: utf-8 -*-

"""
    News views
"""
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from apps.news.models import News
from apps.news.utils import prepare_data_all
from apps.users.models import BaseUser
import datetime

# NOWA WERSJA AKTUALNOŚCI ZE ZMERGOWANYMI SYSTEMAMI PONIZEJ

def all_news(request):
    """
        Latest news
    """

    if BaseUser.is_student(request.user):
        student = request.user.student
        student.last_news_view = datetime.datetime.now()
        student.save()

    elif BaseUser.is_employee(request.user):
        employee = request.user.employee
        employee.last_news_view = datetime.datetime.now()
        employee.save()

    items = News.objects.exclude(category='-')
    paginator = Paginator(items, 15)
    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        news = paginator.page(1)

    data  = {'items': news, 'page_range': paginator.page_range}

    return render_to_response('news/list_all.html', data, context_instance = RequestContext(request))

def main_page( request ):
    """
        Main page
    """
    try:
        news = News.objects.exclude(category='-').select_related('author')[0]
    except ObjectDoesNotExist:
        news = None

    return render_to_response('common/index.html', {'news': news}, context_instance = RequestContext(request))
