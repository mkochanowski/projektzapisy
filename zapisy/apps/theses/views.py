from typing import List
from enum import Enum

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Value, When, Case, BooleanField, QuerySet, Q
from django.db.models.functions import Concat, Lower
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, permissions, exceptions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from dal import autocomplete

from apps.users.models import Student, Employee, BaseUser
from .models import Thesis, ThesisStatus, ThesisKind
from . import serializers
from .drf_permission_classes import ThesisPermissions
from .users import (
    wrap_user, get_theses_board, get_user_type,
    get_theses_user_full_name, ThesisUserType,
    is_student
)

"""Names of processing parameters in query strings"""
THESIS_TYPE_FILTER_NAME = "type"
THESIS_TITLE_FILTER_NAME = "title"
THESIS_ADVISOR_FILTER_NAME = "advisor"
ONLY_MINE_THESES_PARAM_NAME = "only_mine"
THESIS_SORT_COLUMN_NAME = "column"
THESIS_SORT_DIR_NAME = "dir"


class ThesisTypeFilter(Enum):
    """Various values for the "thesis type" filter in the main UI view
    Must match values in backend_callers.ts (this is what client code
    will send to us)
    """
    EVERYTHING = 0
    CURRENT = 1
    ARCHIVED = 2
    MASTERS = 3
    ENGINEERS = 4
    BACHELORS = 5
    BACHELORS_OR_ENGINEERS = 6
    ISIM = 7
    AVAILABLE_MASTERS = 8
    AVAILABLE_ENGINEERS = 9
    AVAILABLE_BACHELORS = 10
    AVAILABLE_BACHELORS_OR_ENGINEERS = 11
    AVAILABLE_ISIM = 12

    DEFAULT = EVERYTHING


class ThesesPagination(LimitOffsetPagination):
    default_limit = 30


class ThesesViewSet(viewsets.ModelViewSet):
    # NOTICE if you change this, you might also want to change the permission class
    http_method_names = ["patch", "get", "post", "delete"]
    permission_classes = (ThesisPermissions,)
    serializer_class = serializers.ThesisSerializer
    pagination_class = ThesesPagination

    def get_queryset(self) -> QuerySet:
        requested_thesis_type_str = self.request.query_params.get(THESIS_TYPE_FILTER_NAME, None)

        try:
            if requested_thesis_type_str:
                requested_thesis_type = ThesisTypeFilter(int(requested_thesis_type_str))
            else:
                requested_thesis_type = ThesisTypeFilter.DEFAULT
        except ValueError:
            raise exceptions.ParseError(f'Unknown filter value {requested_thesis_type_str}')

        requested_thesis_title = self.request.query_params.get(
            THESIS_TITLE_FILTER_NAME, ""
        ).strip()
        requested_advisor_name = self.request.query_params.get(
            THESIS_ADVISOR_FILTER_NAME, ""
        ).strip()
        only_mine = self.request.query_params.get(
            ONLY_MINE_THESES_PARAM_NAME, "0"
        ) == "1"

        sort_column = self.request.query_params.get(THESIS_SORT_COLUMN_NAME, "")
        sort_dir = self.request.query_params.get(THESIS_SORT_DIR_NAME, "")

        base_qs = generate_base_queryset()
        wrapped_user = wrap_user(self.request.user)
        filtered = filter_queryset(
            base_qs, wrapped_user,
            requested_thesis_type, requested_thesis_title,
            requested_advisor_name, only_mine,
        )
        return sort_queryset(filtered, sort_column, sort_dir)


def generate_base_queryset() -> QuerySet:
    """Return theses queryset with the appropriate fields prefetched (see below)
    as well as user names annotated for further processing - sorting/filtering
    """
    return Thesis.objects.select_related(
        *fields_for_prefetching("student"),
        *fields_for_prefetching("student_2"),
        *fields_for_prefetching("advisor"),
        *fields_for_prefetching("auxiliary_advisor"),
    ).annotate(
        _advisor_name=Concat(
            "advisor__user__first_name", Value(" "), "advisor__user__last_name"
        )
    ).annotate(_is_archived=Case(
        When(status=ThesisStatus.DEFENDED.value, then=True),
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
    qs: QuerySet, user: BaseUser,
    thesis_type: ThesisTypeFilter, title: str, advisor_name: str, only_mine: bool,
) -> QuerySet:
    """Filter the specified theses queryset based on the passed conditions"""
    result = filter_theses_queryset_for_type(qs, thesis_type)
    result = filter_theses_queryset_for_user(qs, user)
    if only_mine:
        result = filter_theses_queryset_for_only_mine(result, user)
    if title:
        result = result.filter(title__icontains=title)
    if advisor_name:
        result = result.filter(_advisor_name__icontains=advisor_name)
    return result


def sort_queryset(qs: QuerySet, sort_column: str, sort_dir: str) -> QuerySet:
    """Sort the specified queryset first by archived status (unarchived theses first),
    then by the specified column in the specified direction,
    or by newest first if not specified
    """
    db_column = ""
    if sort_column == "advisor":
        db_column = "_advisor_name"
    elif sort_column == "title":
        db_column = "title"

    resulting_ordering = "-modified_date"
    if db_column:
        orderer = Lower(db_column)
        resulting_ordering = orderer.desc() if sort_dir == "desc" else orderer.asc()

    # We want to first order by archived
    return qs.order_by("_is_archived", resulting_ordering)


def available_thesis_filter(qs: QuerySet) -> QuerySet:
    """Returns only theses that are considered "available" from the specified queryset"""
    return qs.exclude(
        status=ThesisStatus.IN_PROGRESS.value
    ).exclude(_is_archived=True).filter(reserved_until__isnull=True)


# Determines the thesis kinds that match given filter values
# i.e. if the user asks for all engineer theses, we assume they want
# all theses suitable for engineer degrees, so bachelors+engineers should
# be returned as well
ENGINEERS_KINDS = tuple(k.value for k in (
    ThesisKind.ENGINEERS, ThesisKind.BACHELORS_ENGINEERS, ThesisKind.BACHELORS_ENGINEERS_ISIM
))
BACHELORS_KINDS = tuple(k.value for k in(
    ThesisKind.BACHELORS, ThesisKind.BACHELORS_ENGINEERS, ThesisKind.BACHELORS_ENGINEERS_ISIM
))
BACHELORS_OR_ENGINEERS_KINDS = tuple(set(ENGINEERS_KINDS + BACHELORS_KINDS))
ISIM_KINDS = (k.value for k in (
    ThesisKind.ISIM, ThesisKind.BACHELORS_ENGINEERS_ISIM
))


def filter_theses_queryset_for_type(qs: QuerySet, thesis_type: ThesisTypeFilter) -> QuerySet:
    """Returns only theses matching the specified type filter from the specified queryset"""
    if thesis_type == ThesisTypeFilter.EVERYTHING:
        return qs
    elif thesis_type == ThesisTypeFilter.CURRENT:
        return qs.exclude(_is_archived=True)
    elif thesis_type == ThesisTypeFilter.ARCHIVED:
        return qs.filter(_is_archived=True)
    elif thesis_type == ThesisTypeFilter.MASTERS:
        return qs.filter(kind=ThesisKind.MASTERS.value)
    elif thesis_type == ThesisTypeFilter.ENGINEERS:
        return qs.filter(kind__in=ENGINEERS_KINDS)
    elif thesis_type == ThesisTypeFilter.BACHELORS:
        return qs.filter(kind__in=BACHELORS_KINDS)
    elif thesis_type == ThesisTypeFilter.BACHELORS_OR_ENGINEERS:
        return qs.filter(kind__in=BACHELORS_OR_ENGINEERS_KINDS)
    elif thesis_type == ThesisTypeFilter.ISIM:
        return qs.filter(kind__in=ISIM_KINDS)
    elif thesis_type == ThesisTypeFilter.AVAILABLE_MASTERS:
        return available_thesis_filter(qs.filter(kind=ThesisKind.MASTERS.value))
    elif thesis_type == ThesisTypeFilter.AVAILABLE_ENGINEERS:
        return available_thesis_filter(qs.filter(kind__in=ENGINEERS_KINDS))
    elif thesis_type == ThesisTypeFilter.AVAILABLE_BACHELORS:
        return available_thesis_filter(qs.filter(kind__in=BACHELORS_KINDS))
    elif thesis_type == ThesisTypeFilter.AVAILABLE_BACHELORS_OR_ENGINEERS:
        return available_thesis_filter(qs.filter(kind__in=BACHELORS_OR_ENGINEERS_KINDS))
    elif thesis_type == ThesisTypeFilter.AVAILABLE_ISIM:
        return available_thesis_filter(qs.filter(kind__in=ISIM_KINDS))
    # Should never get here
    return qs


def filter_theses_queryset_for_only_mine(qs: QuerySet, user: BaseUser):
    user_type = get_user_type(user)
    if user_type == ThesisUserType.STUDENT:
        return qs.filter(Q(student=user) | Q(student_2=user))
    return qs.filter(Q(advisor=user) | Q(auxiliary_advisor=user))


NOT_READY_STATUSES = (
    ThesisStatus.BEING_EVALUATED.value,
    ThesisStatus.RETURNED_FOR_CORRECTIONS.value
)


def filter_theses_queryset_for_user(qs: QuerySet, user: BaseUser):
    """Filter the queryset based on special logic depending
    on the type of the user
    """
    # Students should not see theses that are not "ready" yet
    if is_student(user):
        return qs.exclude(status__in=NOT_READY_STATUSES)
    return qs

class ThesesBoardViewSet(viewsets.ModelViewSet):
    http_method_names = ["get"]
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.ThesesBoardMemberSerializer

    def get_queryset(self) -> QuerySet:
        return get_theses_board()


class EmployeesViewSet(viewsets.ModelViewSet):
    http_method_names = ["get"]
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.ThesesPersonSerializer

    def get_queryset(self) -> QuerySet:
        return Employee.objects.select_related("user")


@api_view(http_method_names=["get"])
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
                raise PermissionDenied()
            qs = queryset.objects.select_related(
                "user"
            ).annotate(
                _full_name=Concat(
                    "user__first_name", Value(" "), "user__last_name"
                )
            ).order_by("_full_name")
            if self.q:
                qs = qs.filter(_full_name__icontains=self.q)
            return qs.all()

        def get_result_label(self, result):
            """Define how to stringify results; for Employees we want their full name with title"""
            return get_theses_user_full_name(result)
    return ac


StudentAutocomplete = build_autocomplete_view_with_queryset(Student)
EmployeeAutocomplete = build_autocomplete_view_with_queryset(Employee)
