from rest_framework import serializers

from apps.enrollment.courses.models import Classroom, Semester


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
