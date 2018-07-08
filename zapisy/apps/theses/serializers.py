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
        fields = ('id', 'user')

class ThesisSerializer(serializers.ModelSerializer):
    advisor = EmployeeThesesSerializer(read_only=True)

    class Meta:
        model = models.Thesis
        read_only_fields = ('id', 'advisor', 'kind')
        fields = ('id', 'title', 'advisor', 'kind', 'reserved')
