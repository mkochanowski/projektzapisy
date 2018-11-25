from enum import Enum
import sys

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from dal import autocomplete

from apps.users.models import Student, Employee
from .models import Thesis, ThesisStatus, ThesisKind
from . import serializers

THESIS_TYPE_FILTER_NAME = "type"
THESIS_TITLE_FILTER_NAME = "title"
THESIS_ADVISOR_FILTER_NAME = "advisor"


class ThesisTypeFilter(Enum):
    """
    Various values for the "thesis type" filter in the main UI view
    Must match values in backend_callers.ts (this is what client code
    will send to us)
    """
    all_current = 0
    all = 1
    masters = 2
    engineers = 3
    bachelors = 4
    bachelors_isim = 5
    available_masters = 6
    available_engineers = 7
    available_bachelors = 8
    available_bachelors_isim = 9

    default = all_current


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10


class ThesesViewSet(viewsets.ModelViewSet):
    http_method_names = ["patch", "get"]
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = serializers.ThesisSerializer

    def get_queryset(self):
        requested_thesis_type_str = self.request.query_params.get(THESIS_TYPE_FILTER_NAME, None)

        try:
            requested_thesis_type = int(requested_thesis_type_str)\
                if requested_thesis_type_str\
                else ThesisTypeFilter.default.value
        except ValueError:
            raise ParseError()

        requested_thesis_title = self.request.query_params.get(
            THESIS_TITLE_FILTER_NAME, ""
        ).strip()
        requested_advisor_name = self.request.query_params.get(
            THESIS_ADVISOR_FILTER_NAME, ""
        ).strip()

        result = filter_theses_queryset(
            requested_thesis_type, requested_thesis_title, requested_advisor_name
        )
        return result.order_by("-added_date")


def filter_theses_queryset(thesis_type: ThesisTypeFilter, title: str, advisor_name: str):
    result = Thesis.objects.select_related(
        "student", "student_2", "advisor", "auxiliary_advisor",
        "student__user", "student_2__user", "advisor__user", "auxiliary_advisor__user",
    ).all()
    result = filter_theses_queryset_for_type(result, thesis_type)
    if title:
        result = result.filter(title__icontains=title)

    if advisor_name:
        emp_filtered_theses_ids = [
            t.id for t in result
            if advisor_name.lower() in t.advisor.get_full_name().lower()
        ]
        result = result.filter(advisor__id__in=emp_filtered_theses_ids)

    print(f'{result.count()} theses')
    return result


def available_thesis_filter(queryset):
    return queryset\
        .exclude(status=ThesisStatus.in_progress.value)\
        .exclude(status=ThesisStatus.defended.value)\
        .exclude(reserved=True)


def filter_theses_queryset_for_type(queryset, thesis_type):
    if thesis_type == ThesisTypeFilter.all_current.value:
        return queryset.exclude(status=ThesisStatus.defended.value)
    elif thesis_type == ThesisTypeFilter.all.value:
        return queryset
    elif thesis_type == ThesisTypeFilter.masters.value:
        return queryset.filter(kind=ThesisKind.masters.value)
    elif thesis_type == ThesisTypeFilter.engineers.value:
        return queryset.filter(kind=ThesisKind.engineers.value)
    elif thesis_type == ThesisTypeFilter.bachelors.value:
        return queryset.filter(kind=ThesisKind.bachelors.value)
    elif thesis_type == ThesisTypeFilter.bachelors_isim.value:
        return queryset.filter(kind=ThesisKind.isim.value)
    elif thesis_type == ThesisTypeFilter.available_masters.value:
        return available_thesis_filter(queryset.filter(kind=ThesisKind.masters.value))
    elif thesis_type == ThesisTypeFilter.available_engineers.value:
        return available_thesis_filter(queryset.filter(kind=ThesisKind.engineers.value))
    elif thesis_type == ThesisTypeFilter.available_bachelors.value:
        return available_thesis_filter(queryset.filter(kind=ThesisKind.bachelors.value))
    elif thesis_type == ThesisTypeFilter.available_bachelors_isim.value:
        return available_thesis_filter(queryset.filter(kind=ThesisKind.isim.value))
    else:
        raise ParseError()


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
