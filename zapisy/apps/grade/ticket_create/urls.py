from django.urls import path
from . import views

urlpatterns = [
    path('ajax_keys_progress', views.ajax_keys_progress, name='grade-ticket-keys-progress'),
    path('ajax_keys_generate', views.ajax_keys_generate, name='grade-ticket-keys-generator'),
    path('get-poll-data', views.get_poll_data, name='grade-ticket-get-poll-data'),
    path('sign-tickets', views.sign_tickets, name='grade-ticket-sign-tickets'),
    path('keys_generate', views.keys_generate, name='grade-ticket-keys-generate'),
    path('tickets_generate', views.tickets_generate, name='grade-ticket-tickets-generate')
]
