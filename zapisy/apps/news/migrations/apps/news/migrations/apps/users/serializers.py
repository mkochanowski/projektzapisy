from django.contrib.auth.models import User
from rest_framework import serializers
from apps.users.models import Student, Employee


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        depth = 1
        fields = ('id', 'matricula', 'user', 'ects')


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
