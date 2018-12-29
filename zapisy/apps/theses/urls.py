from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("theses", views.ThesesViewSet, base_name="theses")
router.register("theses_board", views.ThesesBoardViewSet, base_name="theses_board")

urlpatterns = [
    url(r"^$", views.theses_main, name="main"),
    # for django-autocomplete-light (admin widgets; see forms.py)
    url(
        r"^api/student-autocomplete/$",
        views.StudentAutocomplete.as_view(),
        name="student-autocomplete",
    ),
    url(
        r"^api/employee-autocomplete/$",
        views.EmployeeAutocomplete.as_view(),
        name="employee-autocomplete",
    ),
    url(r"^api/current_user/$", views.get_current_user, name="current_user"),
    url(r"^api/", include(router.urls))
]
