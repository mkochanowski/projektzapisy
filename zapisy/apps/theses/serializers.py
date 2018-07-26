from rest_framework import serializers

from . import models
from apps.users.models import Employee, Student
from apps.api.rest.v1.serializers import UserSerializer
from .errors import InvalidQueryError


class PersonSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "display_name": instance.get_full_name(),
        }

    def to_internal_value(self, data):
        person_id = data.get("id")
        if type(person_id) is not int or person_id < 0:
            raise serializers.ValidationError({
                "id": "Expected 'id' to be a valid positive integer"
            })
        return {"id": person_id}


class ThesisSerializer(serializers.ModelSerializer):
    advisor = PersonSerializer()
    auxiliary_advisor = PersonSerializer()
    student = PersonSerializer()
    student_2 = PersonSerializer()
    added_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")
    modified_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")

    def _update_advisors(self, instance, validated_data):
        if "advisor" in validated_data:
            instance.advisor = _get_person_from_queryset(Employee, validated_data.get("advisor"))
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
        instance.title = validated_data.get('title', instance.title)
        instance.kind = validated_data.get('kind', instance.kind)
        instance.reserved = validated_data.get('reserved', instance.reserved)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        self._update_advisors(instance, validated_data)
        self._update_students(instance, validated_data)
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
    except queryset.DoesNotExist:
        raise InvalidQueryError("Bad person ID specified")
