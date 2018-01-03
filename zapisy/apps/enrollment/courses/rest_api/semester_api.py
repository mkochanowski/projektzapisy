from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from enrollment.courses.models.semester import Semester


class SimpleSemesterSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Semester
        fields = ('id', 'display_name')

    def get_display_name(self, obj):
        return 'Semestr {} {}'.format(obj.year, obj.type)


@api_view(['GET'])
def get_semester_list(request):
    semesters = Semester.objects.all()
    serializer = SimpleSemesterSerializer(semesters, many=True)

    return Response(serializer.data)
