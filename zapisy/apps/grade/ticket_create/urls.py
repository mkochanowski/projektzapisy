from django.urls import path
from . import views

urlpatterns = [
    path('get-poll-data', views.get_poll_data, name='grade-ticket-get-poll-data'),
    path('sign-tickets', views.sign_tickets, name='grade-ticket-sign-tickets'),
    path('keys-generate', views.keys_generate, name='grade-ticket-keys-generate'),
    path('tickets-generate', views.tickets_generate, name='grade-ticket-tickets-generate')
]
