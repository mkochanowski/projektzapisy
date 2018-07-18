from rest_framework import serializers

from . import models
from apps.users.models import Employee, Student
from apps.api.rest.v1.serializers import UserSerializer
from .errors import InvalidQueryError


# We just need the employee's ID and their .user field
class EmployeeThesesSerializer(serializers.RelatedField):
    def get_queryset(self):
        return None
    
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "username": instance.user.username,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name
        }

    def to_internal_value(self, data):
        print("Employee TO INTERNAL VALUE")
        empid = data.get("id")
        if type(empid) is not int or empid < 0:
            raise serializers.ValidationError({
                "id": "Expected 'id' to be a valid positive integer"
            })
        return { "id": empid }

class ThesisSerializer(serializers.ModelSerializer):
    advisor = EmployeeThesesSerializer()
    auxiliary_advisor = EmployeeThesesSerializer()
    added_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")
    modified_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")

    def _update_advisors(self, instance, validated_data):
        print("Update advisors", validated_data)
        if "advisor" in validated_data:
            print("Will try to update advisor", validated_data.get("advisor"))
            instance.advisor = _get_person_from_queryset(Employee, validated_data.get("advisor"))
            print("new advisor", instance.advisor)
        if "auxiliary_advisor" in validated_data:
            if not instance.advisor:
                raise InvalidQueryError("Cannot set auxiliary advisor without an advisor present")
            instance.auxiliary_advisor = _get_person_from_queryset(Employee, validated_data.get("auxiliary_advisor"))

    def _update_students(self, instance, validated_data):
        if "student" in validated_data:
            instance.student = _get_person_from_queryset(Student, validated_data.get("student"))
        if "student_2" in validated_data:
            if not instance.student:
                raise InvalidQueryError("Cannot set second student without a student present")
            instance.student_2 = _get_person_from_queryset(Student, validated_data.get("student_2"))

    def update(self, instance, validated_data):
        print("UPDATE", validated_data)
        instance.title = validated_data.get('title', instance.title)
        instance.kind = validated_data.get('kind', instance.kind)
        instance.reserved = validated_data.get('reserved', instance.reserved)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        #self._update_advisors(instance, validated_data)
        # self._update_students(instance, validated_data)
        instance.save()
        return instance

    class Meta:
        model = models.Thesis
        read_only_fields = ('id', 'kind')
        fields = (
            'id', 'title', 'advisor', 'auxiliary_advisor',
            'kind', 'reserved', 'description', 'status',
            'student', 'student_2', 'added_date', 'modified_date',
        )


def _get_person_from_queryset(queryset, person_data):
    print("get person:", person_data)
    if "id" not in person_data:
        raise InvalidQueryError("Missing person ID")
    try:
        return queryset.objects.get(pk=person_data.get("id"))
    except:
        raise InvalidQueryError("Bad person ID specified")
