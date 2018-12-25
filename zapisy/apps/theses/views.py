from typing import List

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from dal import autocomplete

from apps.users.models import Student, Employee
from .models import Thesis
from . import serializers
from .drf_permission_classes import ThesisPermissions
from .users import wrap_user


class ThesesViewSet(viewsets.ModelViewSet):
    # NOTICE if you change this, you might also want to change the permission class
    http_method_names = ["patch", "get", "post"]
    permission_classes = (ThesisPermissions,)
    serializer_class = serializers.ThesisSerializer

    def get_queryset(self):
        result = Thesis.objects.select_related(
            *fields_for_prefetching("student"),
            *fields_for_prefetching("student_2"),
            *fields_for_prefetching("advisor"),
            *fields_for_prefetching("auxiliary_advisor"),
        ).all()
        return result.order_by("-added_date")


def fields_for_prefetching(base_field: str) -> List[str]:
    """For all user fields present on the thesis, we need to prefetch
    both our user model and the standard Django user it's linked to; see
    users.wrap_user for a more detailed explanation"""
    return [base_field, f'{base_field}__user']


@api_view()
@permission_classes((permissions.IsAuthenticated,))
def get_current_user(request):
    """Allows the front end to query the current thesis user role"""
    wrapped_user = wrap_user(request.user)
    serializer = serializers.CurrentUserSerializer(wrapped_user)
    return Response(serializer.data)


@login_required
def theses_main(request):
    return render(request, "theses/main.html")


def build_autocomplete_view_with_queryset(queryset):
    """Given a queryset, build an autocomplete view for django-autocomplete-light
    (forms.py explains why we use it)
    """
    class ac(autocomplete.Select2QuerySetView):
        def get_queryset(self):
            if not self.request.user.is_authenticated:
                return queryset.objects.none()
            qs = queryset.objects.all().select_related("user")
            if self.q:
                qs = qs.filter(
                    Q(user__first_name__istartswith=self.q) | Q(user__last_name__istartswith=self.q)
                )
            return qs
    return ac


StudentAutocomplete = build_autocomplete_view_with_queryset(Student)
EmployeeAutocomplete = build_autocomplete_view_with_queryset(Employee)
