from django.urls import path
from . import views

urlpatterns = [
    path("", views.TicketsEntry.as_view(), name="grade-poll-v2-index"),
    path("enter", views.TicketsEntry.as_view(), name="grade-poll-v2-tickets-enter"),
    path("submissions", views.SubmissionEntry.as_view(), name="grade-poll-v2-submissions"),
    path("results", views.PollResults.as_view(), name="grade-poll-v2-results"),
    path("schemas", views.SchemasManagement.as_view(), name="grade-poll-v2-schemas"),
]

