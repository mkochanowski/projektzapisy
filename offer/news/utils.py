# -*- coding: utf-8 -*-
"""
Various utils.
"""

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.template import Context, RequestContext
from django.template.loader import get_template
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet
from mailer import send_html_mail

from offer.news.models import News
from users.models import Employee, Student

MASS_MAIL_FROM = 'noreply@example.com'
NEWS_PER_PAGE = 5

def render_items(request, items):
    """
        Renders items
    """
    con = RequestContext(request, {
        'object_list':items,
    } )
    tem = get_template('offer/news/ajax_list.html')
    return tem.render(con)

def render_newer_group(beginwith, quantity):
    """
        Renders newer group
    """
    con = Context( {
        'newer_no':quantity,
        'newer_beginwith':beginwith,
    } )
    tem = get_template('offer/news/newer_group.html')
    return tem.render(con)

def render_older_group(beginwith, quantity):
    """
        Renders older group
    """
    con = Context( {
        'older_no':quantity,
        'older_beginwith':beginwith,
    } )
    tem = get_template('offer/news/older_group.html')
    return tem.render(con)

def prepare_data(request, items,
                 beginwith=0, quantity=NEWS_PER_PAGE,
                 archive_view=False):
    """
        Prepares data
    """
    news_count = News.objects.count()
    data = {}
    data['content']     = render_items(request, items)
    data['older_group'] = render_older_group(
        beginwith + quantity, 
        max(news_count-(beginwith+quantity),0))
    data['newer_group'] = render_newer_group(
        max(beginwith - quantity, 0),
        beginwith)
    data['archive_view'] = archive_view
    data['search_view']  = False
    return data

def render_search_newer_group(page, query):
    """
        Renders search result
    """
    con = Context( {
        'page':  page,
        'query': query,
    } )
    tem = get_template('offer/news/search_newer_group.html')
    return tem.render(con)

def render_search_older_group(page, query):
    """
        Renders search result
    """
    con = Context( {
        'page':  page,
        'query': query,
    } )
    tem = get_template('offer/news/search_older_group.html')
    return tem.render(con)

def get_search_results_data(request):
    """
        Gets search result
    """
    try:
        page_n = request.GET.get('page', 1)
        sqs  = SearchQuerySet().order_by('-date')
        form = SearchForm(request.GET, searchqueryset=sqs,
                          load_all=False)
        if 'q' in request.GET and request.GET['q'] and form.is_valid():
            query = form.cleaned_data['q']
            results = map(lambda r: r.object, form.search())
            paginator = Paginator(results, NEWS_PER_PAGE)
            page = paginator.page(page_n)
            data = {}
            data['content'] = render_items(request, page.object_list)
            data['newer_group']  = render_search_newer_group(page, query)
            data['older_group']  = render_search_older_group(page, query)
            data['archive_view'] = False
            data['search_view']  = True
            return data
        else:
            msg = "Niewłaściwe zapytanie"
            data = {'message': msg}
            return data
    except InvalidPage:
        raise Http404

def render_email_from_news(news):
    """
    Creates multipart email message given a news instance.

    Returns (subject, text_body, html_body) triple.
    """
    con = Context( {
        'news':  news,
        'news_url': "http://" +
                  str(Site.objects.get_current().domain) +
                  reverse('news-item', args=[news.id])
    } )
    tem = get_template('offer/news/email_plaintext.html')
    plaintext_body = tem.render(con)
    tem = get_template('offer/news/email_html.html')
    html_body = tem.render(con)
    from_email = MASS_MAIL_FROM
    subject = settings.EMAIL_SUBJECT_PREFIX + news.title
    return (subject, plaintext_body, html_body)

def send_mass_mail_to_employees(msg_parts):
    """
    Queue mass mail to employees who haven't opted out.
    """
    (subject, text_body, html_body) = msg_parts
    emails = [emp.user.email for emp in
              Employee.objects.filter(receive_mass_mail_offer=True)]
    for email in emails:
        send_html_mail(subject, text_body, html_body, 
                       MASS_MAIL_FROM, [email])
                       
def send_mass_mail_to_students(msg_parts):
    """
    Queue mass mail to students who haven't opted out.
    """
    (subject, text_body, html_body) = msg_parts
    emails = [emp.user.email for emp in
              Student.objects.filter(receive_mass_mail_offer=True)]
    for email in emails:
        send_html_mail(subject, text_body, html_body, 
                       MASS_MAIL_FROM, [email])

def mail_news_to_employees(news):
    """
    Queue news in form of a mail message to all employees
    that haven't opted out.
    """
    send_mass_mail_to_employees(render_email_from_news(news))
    
def mail_news_to_students(news):
    """
    Queue news in form of a mail message to all students
    that haven't opted out.
    """
    send_mass_mail_to_students(render_email_from_news(news))
