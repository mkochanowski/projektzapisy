from enum import Enum

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from dal import autocomplete

from apps.users.models import Student, Employee
from . import models
from . import serializers
from .errors import InvalidQueryError

THESIS_TYPE_FILTER_NAME = "thesis_type"

"""
Various values for the "thesis type" filter in the main UI view
Must match values in backend_callers.ts (this is what client code
will send to us)
"""
class ThesisTypeFilter(Enum):
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

class ThesesViewSet(viewsets.ModelViewSet):
    http_method_names = ["patch", "get"]
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = serializers.ThesisSerializer

    def get_queryset(self):
        result = models.Thesis.objects.all()
        requested_thesis_type_str = self.request.query_params.get(THESIS_TYPE_FILTER_NAME, None)
        if requested_thesis_type_str is None:
            return result
        
        try:
            requested_thesis_type = int(requested_thesis_type_str)
            return filter_theses_queryset_for_type(result, requested_thesis_type)
        except ValueError:
            raise ParseError()


def available_thesis_filter(queryset):
    return queryset\
        .exclude(status=models.ThesisStatus.in_progress.value)\
        .exclude(status=models.ThesisStatus.defended.value)\
        .exclude(reserved=True)

def filter_theses_queryset_for_type(queryset, thesis_type):
    if thesis_type == ThesisTypeFilter.all_current.value:
        return queryset.exclude(status=models.ThesisStatus.defended.value)
    elif thesis_type == ThesisTypeFilter.all.value:
        return queryset
    elif thesis_type == ThesisTypeFilter.masters.value:
        return queryset.filter(kind=models.ThesisKind.masters.value)
    elif thesis_type == ThesisTypeFilter.engineers.value:
        return queryset.filter(kind=models.ThesisKind.engineers.value)
    elif thesis_type == ThesisTypeFilter.bachelors.value:
        return queryset.filter(kind=models.ThesisKind.bachelors.value)
    elif thesis_type == ThesisTypeFilter.bachelors_isim.value:
        return queryset.filter(kind=models.ThesisKind.isim.value)
    elif thesis_type == ThesisTypeFilter.available_masters.value:
        return available_thesis_filter(queryset.filter(kind=models.ThesisKind.masters.value))
    elif thesis_type == ThesisTypeFilter.available_engineers.value:
        return available_thesis_filter(queryset.filter(kind=models.ThesisKind.engineers.value))
    elif thesis_type == ThesisTypeFilter.available_bachelors.value:
        return available_thesis_filter(queryset.filter(kind=models.ThesisKind.bachelors.value))
    elif thesis_type == ThesisTypeFilter.available_bachelors_isim.value:
        return available_thesis_filter(queryset.filter(kind=models.ThesisKind.isim.value))
    else:
        raise ParseError()

@login_required
def theses_main(request):
    return render(request, "theses/main.html")

def build_autocomplete_view_with_queryset(queryset):
    class ac(autocomplete.Select2QuerySetView):
        def get_queryset(self):
            if not self.request.user.is_authenticated():
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
