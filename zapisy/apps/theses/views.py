from typing import List

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from dal import autocomplete

from apps.users.models import Student, Employee
from .models import Thesis, get_num_ungraded_for_emp
from . import serializers
from .drf_permission_classes import ThesisPermissions
from .utils import wrap_user
from .users import ThesisUserType, get_theses_board, get_user_type


class ThesesViewSet(viewsets.ModelViewSet):
    # NOTICE if you change this, you might also want to change the permission class
    http_method_names = ["patch", "get", "post"]
    permission_classes = (ThesisPermissions,)
    serializer_class = serializers.ThesisSerializer

    def get_queryset(self):
        return Thesis.objects\
            .order_by("-added_date")\
            .select_related(
                *fields_for_prefetching("student"),
                *fields_for_prefetching("student_2"),
                *fields_for_prefetching("advisor"),
                *fields_for_prefetching("auxiliary_advisor"),
            )\
            .prefetch_related("votes")\
            .prefetch_related("votes__voter")\
            .all()


def fields_for_prefetching(base_field: str) -> List[str]:
    return [base_field, f'{base_field}__user']


class ThesesBoardViewSet(viewsets.ModelViewSet):
    http_method_names = ["get"]
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = serializers.ThesesBoardMemberSerializer

    def get_queryset(self):
        return get_theses_board()


@api_view(http_method_names=["get"])
@permission_classes((permissions.IsAuthenticated,))
def get_current_user(request):
    wrapped_user = wrap_user(request.user)
    serializer = serializers.CurrentUserSerializer(wrapped_user)
    return Response(serializer.data)


@api_view(http_method_names=["get"])
@permission_classes((permissions.IsAuthenticated,))
def get_num_ungraded(request):
    wrapped_user = wrap_user(request.user)
    user_type = get_user_type(wrapped_user)
    if user_type != ThesisUserType.theses_board_member:
        raise NotFound()
    return Response(get_num_ungraded_for_emp(wrapped_user))


@login_required
def theses_main(request):
    return render(request, "theses/main.html")


def build_autocomplete_view_with_queryset(queryset):
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
