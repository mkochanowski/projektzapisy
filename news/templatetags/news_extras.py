# -*- coding: utf-8 -*-

from django import template
from libs import postmarkup

register = template.Library()

from news.models import News

@register.simple_tag
def newscount(category):
    """Wyświetla liczbę nowych ogłoszeń."""
    return(str(News.objects.count_new(category)))
    
@register.filter
def bbcode(str):

    markup = postmarkup.PostMarkup()
    
    markup.add_tag(postmarkup.SimpleTag, u'b', u'strong')
    markup.add_tag(postmarkup.SimpleTag, u'i', u'em')
    markup.add_tag(postmarkup.SimpleTag, u'u', u'u')
    markup.add_tag(postmarkup.SimpleTag, u's', u's')

    return markup.render_to_html(str)

@register.filter
def nl2br(str):
    return str.replace("\n", "<br />")
    
