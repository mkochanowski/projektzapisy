from django.conf.urls import include, url
from .poll import views as poll_views
from django.views.generic import TemplateView

# to tree/list_view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = [
    url(r'^$', poll_views.GradeDetails.as_view(), name="grade-main"),
    url("poll/", include("apps.grade.poll.urls")),
    url("ticket/", include("apps.grade.ticket_create.urls")),
]
