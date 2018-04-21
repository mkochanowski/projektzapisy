from rest_framework import serializers

from apps.enrollment.courses.models import Classroom, Semester
from apps.users.models import Employee

from django.contrib.auth.models import User


class SemesterSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Semester
        fields = ('id', 'display_name')

    def get_display_name(self, obj):
        return obj.get_name()


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ('id', 'type', 'description', 'number', 'order', 'building', 'capacity',
                  'floor', 'can_reserve', 'slug')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = '__all__'
