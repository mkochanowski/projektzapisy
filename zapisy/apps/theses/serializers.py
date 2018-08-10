from enum import Enum

from rest_framework import serializers

from . import models
from apps.users.models import Employee, Student
from apps.api.rest.v1.serializers import UserSerializer
from .errors import InvalidQueryError
from apps.users.models import BaseUser


class ThesisUserType(Enum):
    student = 0
    employee = 1
    theses_board_member = 2
    admin = 3


class PersonSerializerForThesis(serializers.Serializer):
    """
    Used to serialize employee/student fields in the thesis model
    """
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
    advisor = PersonSerializerForThesis(allow_null=True)
    auxiliary_advisor = PersonSerializerForThesis(allow_null=True)
    student = PersonSerializerForThesis(allow_null=True)
    student_2 = PersonSerializerForThesis(allow_null=True)
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
        read_only_fields = ('id', )
        fields = (
            'id', 'title', 'advisor', 'auxiliary_advisor',
            'kind', 'reserved', 'description', 'status',
            'student', 'student_2', 'added_date', 'modified_date',
        )


def _get_person_from_queryset(queryset, person_data):
    if person_data is None:
        return None
    if "id" not in person_data:
        raise InvalidQueryError("Missing person ID")
    try:
        return queryset.objects.get(pk=person_data.get("id"))
    except queryset.DoesNotExist:
        raise InvalidQueryError("Bad person ID specified")


class CurrentUserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: BaseUser):
        return {
            "id": instance.pk,
            "type": CurrentUserSerializer.get_user_type(instance).value
        }

    @staticmethod
    def get_user_type(user_instance: BaseUser) -> ThesisUserType:
        # FIXME is this correct?
        if user_instance.is_staff:
            return ThesisUserType.admin
        elif BaseUser.is_employee(user_instance):
            return (
                ThesisUserType.theses_board_member
                if models.is_theses_board_member(user_instance.employee)
                else ThesisUserType.employee
            )
        elif BaseUser.is_student(user_instance):
            return ThesisUserType.student
