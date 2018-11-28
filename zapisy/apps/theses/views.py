import sys
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


class ThesesViewSet(viewsets.ModelViewSet):
    http_method_names = ["patch", "get"]
    permission_classes = (permissions.DjangoModelPermissions,)
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
    return [base_field, f'{base_field}__user']


@api_view()
@permission_classes((permissions.IsAuthenticated,))
def get_current_user(request):
    serializer = serializers.CurrentUserSerializer(request.user)
    return Response(serializer.data)


@login_required
def theses_main(request):
    return render(request, "theses/main.html")


def build_autocomplete_view_with_queryset(queryset):
    class ac(autocomplete.Select2QuerySetView):
        def get_paginate_by(self, queryset):
            all_pages = self.request.GET.get("allpages", None)
            if all_pages == "1":
                return sys.maxsize
            return super(ac, self).get_paginate_by(queryset)

        def get_queryset(self):
            if not self.request.user.is_authenticated:
                return queryset.objects.none()

            qs = queryset.objects.all()

            if self.q:
                qs = qs.filter(
                    Q(user__first_name__istartswith=self.q) | Q(user__last_name__istartswith=self.q)
                )

            return qs
    return ac


StudentAutocomplete = build_autocomplete_view_with_queryset(Student)
EmployeeAutocomplete = build_autocomplete_view_with_queryset(Employee)
