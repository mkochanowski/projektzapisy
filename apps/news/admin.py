# -*- coding: utf-8 -*-

"""
    News admin
"""

from apps.news.models import News
from django.contrib import admin

class NewsAdmin(admin.ModelAdmin):
    """
        News admin manager
    """
    fields = ('title', 'body', 'author', 'category')
    list_display = ('title', 'date')
    list_filter  = ['date']

    class Media:
        js = ('/site_media/js/tiny_mce/tiny_mce.js',
              '/site_media/js/textareas.js',)

admin.site.register(News, NewsAdmin)
