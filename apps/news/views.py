# -*- coding: utf-8 -*-

"""
    News views
"""
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from apps.news.models import News
from apps.news.utils import prepare_data_all
import datetime

# NOWA WERSJA AKTUALNOŚCI ZE ZMERGOWANYMI SYSTEMAMI PONIZEJ

def all_news(request):
    """
        Latest news
    """

    if hasattr(request.user, 'student'):
        student = request.user.student
        student.last_news_view = datetime.datetime.now()
        student.save()

    elif hasattr(request.user, 'employee'):
        employee = request.user.employee
        employee.last_news_view = datetime.datetime.now()
        employee.save()

    items = News.objects.exclude(category='-')
    data  = {'items': items}

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

