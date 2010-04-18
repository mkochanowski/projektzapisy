# -*- coding: utf-8 -*-

from django import template

register = template.Library()

from fereol.offer.news.models import News

@register.simple_tag
def newscount():
    """Wyświetla liczbę nowych ogłoszeń."""
    return(str(News.objects.count_new()))
    
