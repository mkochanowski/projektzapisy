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
from .users import wrap_user, ThesisUserType, get_theses_board, get_user_type


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
    wrapped_user = wrap_user(request.user)
    user_type = get_user_type(wrapped_user)
    if user_type != ThesisUserType.theses_board_member:
        raise NotFound()
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
