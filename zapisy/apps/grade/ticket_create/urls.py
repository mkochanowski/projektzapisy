from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ajax_keys_progress$', views.ajax_keys_progress, name='grade-ticket-keys-progress'),
    url(r'^ajax_keys_generate$', views.ajax_keys_generate, name='grade-ticket-keys-generator'),
    url(r'^ajax_get_keys$', views.ajax_get_rsa_keys, name='grade-ticket-get-keys'),
    url(r'^ajax_sign_tickets$', views.ajax_sign_tickets, name='grade-ticket-ajax-sign-tickets'),
    url(r'^keys_generate$', views.keys_generate, name='grade-ticket-keys-generate'),

    # feature do poprawienia w przyszłości
    url(r'^tickets_generate$', views.tickets_generate, name='grade-ticket-tickets-generate')
]
