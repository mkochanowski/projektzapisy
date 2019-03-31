from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ajax_keys_progress$', views.ajax_keys_progress, name='grade-ticket-keys-progress'),
    url(r'^ajax_keys_generate$', views.ajax_keys_generate, name='grade-ticket-keys-generator'),
    url(r'^get-poll-data$', views.get_poll_data, name='grade-ticket-get-poll-data'),
    url(r'^sign-tickets$', views.sign_tickets, name='grade-ticket-sign-tickets'),
    url(r'^keys_generate$', views.keys_generate, name='grade-ticket-keys-generate'),
    url(r'^tickets_generate$', views.tickets_generate, name='grade-ticket-tickets-generate')
]
