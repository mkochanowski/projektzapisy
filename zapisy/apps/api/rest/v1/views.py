from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from apps.enrollment.courses.models import Semester, Classroom
from apps.users.models import Employee
from apps.users.utils import StaffPermission

from .serializers import SemesterSerializer, ClassroomSerializer, EmployeeSerializer


class SemesterViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Semester.objects.order_by('-semester_beginning')
    serializer_class = SemesterSerializer


class ClassroomViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (StaffPermission,)
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
