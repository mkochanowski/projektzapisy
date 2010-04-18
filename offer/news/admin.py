# -*- coding: utf-8 -*-

from offer.news.models import News
from django.contrib import admin

class NewsAdmin(admin.ModelAdmin):
    fields = ('title', 'body', 'author')
    list_display = ('title', 'date')
    list_filter  = ['date']

admin.site.register(News, NewsAdmin)
