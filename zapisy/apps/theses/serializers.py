from rest_framework import serializers

from . import models
from apps.users.models import Employee
from apps.api.rest.v1.serializers import UserSerializer

# We just need the employee's ID and their .user field
class EmployeeThesesSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        read_only_fields = ('id', 'user')
        fields = ('id', 'title', 'user')

class ThesisSerializer(serializers.ModelSerializer):
    advisor = EmployeeThesesSerializer(read_only=True)
    auxiliary_advisor = EmployeeThesesSerializer(read_only=True)
    added_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")
    modified_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")

    class Meta:
        model = models.Thesis
        read_only_fields = ('id', 'kind')
        fields = (
            'id', 'title', 'advisor', 'auxiliary_advisor',
            'kind', 'reserved', 'status', 'student', 'student_2',
            'added_date', 'modified_date',
        )
