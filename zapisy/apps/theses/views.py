from typing import List
from enum import Enum

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Value, When, Case, BooleanField
from django.db.models.functions import Concat, Lower
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions
from rest_framework.pagination import LimitOffsetPagination
from dal import autocomplete

from apps.users.models import Student, Employee
from .models import (
    Thesis, ThesisStatus, ThesisKind,
    get_num_ungraded_for_emp, filter_ungraded_for_emp
)
from . import serializers
from .drf_permission_classes import ThesisPermissions
from .users import wrap_user, get_theses_board, is_theses_board_member

"""Names of processing parameters in query strings"""
THESIS_TYPE_FILTER_NAME = "type"
THESIS_TITLE_FILTER_NAME = "title"
THESIS_ADVISOR_FILTER_NAME = "advisor"
THESIS_SORT_COLUMN_NAME = "column"
THESIS_SORT_DIR_NAME = "dir"


class ThesisTypeFilter(Enum):
    """Various values for the "thesis type" filter in the main UI view
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
    ungraded = 10

    default = all


class ThesesPagination(LimitOffsetPagination):
    default_limit = 30


class ThesesViewSet(viewsets.ModelViewSet):
    # NOTICE if you change this, you might also want to change the permission class
    http_method_names = ["patch", "get", "post"]
    permission_classes = (ThesisPermissions,)
    serializer_class = serializers.ThesisSerializer
    pagination_class = ThesesPagination

    def get_queryset(self):
        requested_thesis_type_str = self.request.query_params.get(THESIS_TYPE_FILTER_NAME, None)

        try:
            requested_thesis_type = \
                ThesisTypeFilter(int(requested_thesis_type_str))\
                if requested_thesis_type_str\
                else ThesisTypeFilter.default
        except ValueError:
            raise exceptions.ParseError()

        requested_thesis_title = self.request.query_params.get(
            THESIS_TITLE_FILTER_NAME, ""
        ).strip()
        requested_advisor_name = self.request.query_params.get(
            THESIS_ADVISOR_FILTER_NAME, ""
        ).strip()

        sort_column = self.request.query_params.get(THESIS_SORT_COLUMN_NAME, "")
        sort_dir = self.request.query_params.get(THESIS_SORT_DIR_NAME, "")

        base_qs = generate_base_queryset()
        wrapped_user = wrap_user(self.request.user)
        filtered = filter_queryset(
            base_qs, wrapped_user,
            requested_thesis_type, requested_thesis_title, requested_advisor_name,
        )
        return sort_queryset(filtered, sort_column, sort_dir)


def generate_base_queryset():
    """Return theses queryset with the appropriate fields prefetched (see below)
    as well as user names annotated for further processing - sorting/filtering
    """
    return Thesis.objects\
        .select_related(
            *fields_for_prefetching("student"),
            *fields_for_prefetching("student_2"),
            *fields_for_prefetching("advisor"),
            *fields_for_prefetching("auxiliary_advisor"),
        )\
        .prefetch_related("votes")\
        .prefetch_related("votes__voter")\
        .annotate(
            advisor_name=Concat(
                "advisor__user__first_name", Value(" "), "advisor__user__last_name"
            )
        )\
        .annotate(is_archived=Case(
            When(status=ThesisStatus.defended.value, then=True),
            default=Value(False),
            output_field=BooleanField()
        ))


def fields_for_prefetching(base_field: str) -> List[str]:
    """For all user fields present on the thesis, we need to prefetch
    both our user model and the standard Django user it's linked to; see
    users.wrap_user for a more detailed explanation

    Note that this hurts performance: DB queries with the __user prefetch
    are roughly two times slower than with just the base thesis fields.
    (Of course, we're only talking about the performance of get_queryset here;
    not prefetching those fields would have disastrous consequences later when
    the serializer accesses them)
    Sadly this is necessary until the User system is refactored.
    """
    return [base_field, f'{base_field}__user']


def filter_queryset(
    qs, user: Employee,
    thesis_type: ThesisTypeFilter, title: str, advisor_name: str
):
    """Filter the specified theses queryset based on the passed conditions"""
    result = filter_theses_queryset_for_type(qs, user, thesis_type)
    if title:
        result = result.filter(title__icontains=title)
    if advisor_name:
        result = result.filter(advisor_name__icontains=advisor_name)
    return result


def sort_queryset(qs, sort_column: str, sort_dir: str):
    """Sort the specified queryset first by archived status (unarchived theses first),
    then by the specified column in the specified direction,
    or by newest first if not specified
    """
    db_column = ""
    if sort_column == "advisor":
        db_column = "advisor_name"
    elif sort_column == "title":
        db_column = "title"

    resulting_ordering = "-added_date"
    if db_column:
        orderer = Lower(db_column)
        resulting_ordering = orderer.desc() if sort_dir == "desc" else orderer.asc()

    # We want to first order by archived
    return qs.order_by("is_archived", resulting_ordering)


def available_thesis_filter(queryset):
    """Returns only theses that are considered "available" from the specified queryset"""
    return queryset\
        .exclude(status=ThesisStatus.in_progress.value)\
        .exclude(is_archived=True)\
        .exclude(reserved=True)


def ungraded_theses_filter(queryset, user: Employee):
    """Returns only theses that are ungraded by the currently logged in board member"""
    if not is_theses_board_member(user):
        raise exceptions.NotFound()
    return filter_ungraded_for_emp(queryset, user)


def filter_theses_queryset_for_type(queryset, user: Employee, thesis_type: ThesisTypeFilter):
    """Returns only theses matching the specified type filter from the specified queryset"""
    if thesis_type == ThesisTypeFilter.all_current:
        return queryset.exclude(is_archived=True)
    elif thesis_type == ThesisTypeFilter.all:
        return queryset
    elif thesis_type == ThesisTypeFilter.masters:
        return queryset.filter(kind=ThesisKind.masters.value)
    elif thesis_type == ThesisTypeFilter.engineers:
        return queryset.filter(kind=ThesisKind.engineers.value)
    elif thesis_type == ThesisTypeFilter.bachelors:
        return queryset.filter(kind=ThesisKind.bachelors.value)
    elif thesis_type == ThesisTypeFilter.bachelors_isim:
        return queryset.filter(kind=ThesisKind.isim.value)
    elif thesis_type == ThesisTypeFilter.available_masters:
        return available_thesis_filter(queryset.filter(kind=ThesisKind.masters.value))
    elif thesis_type == ThesisTypeFilter.available_engineers:
        return available_thesis_filter(queryset.filter(kind=ThesisKind.engineers.value))
    elif thesis_type == ThesisTypeFilter.available_bachelors:
        return available_thesis_filter(queryset.filter(kind=ThesisKind.bachelors.value))
    elif thesis_type == ThesisTypeFilter.available_bachelors_isim:
        return available_thesis_filter(queryset.filter(kind=ThesisKind.isim.value))
    elif thesis_type == ThesisTypeFilter.ungraded:
        return ungraded_theses_filter(queryset, user)
    else:
        raise exceptions.ParseError()


class ThesesBoardViewSet(viewsets.ModelViewSet):
    http_method_names = ["get"]
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.ThesesBoardMemberSerializer

    def get_queryset(self):
        return get_theses_board()


@api_view(http_method_names=["get"])
@permission_classes((permissions.IsAuthenticated,))
def get_current_user(request):
    """Allows the front end to query the current thesis user role"""
    wrapped_user = wrap_user(request.user)
    serializer = serializers.CurrentUserSerializer(wrapped_user)
    return Response(serializer.data)


@api_view(http_method_names=["get"])
@permission_classes((permissions.IsAuthenticated,))
def get_num_ungraded(request):
    """Allows the front end to query the number of ungraded theses for the current user"""
    wrapped_user = wrap_user(request.user)
    if not is_theses_board_member(wrapped_user):
        raise exceptions.NotFound()
    return Response(get_num_ungraded_for_emp(wrapped_user))


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
