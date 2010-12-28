# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # feature do dodania w przyszłości
    url(r'keys_generate$',      'fereol.grade.ticket_create.views.keys_generate',      name='grade-ticket-keys-generate'),
    
    # feature do poprawienia w przyszłości
    url(r'connections_choice$', 'fereol.grade.ticket_create.views.connections_choice', name='grade-ticket-connections-choice'),
    url(r'tickets_save$',       'fereol.grade.ticket_create.views.tickets_save',       name='grade-ticket-tickets-save'),
)
