from django.contrib.auth.models import User
from rest_framework import serializers

from apps.users.models import Employee, Student
from .models import Thesis, ThesisStatus
from .errors import InvalidQueryError
from .user_type import get_user_type
from .permissions import can_set_status, can_set_advisor


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


def copy_if_present(dst, src, key, converter=None):
    if key in src:
        dst[key] = converter(src[key]) if converter else src[key]


class ThesisSerializer(serializers.ModelSerializer):
    advisor = PersonSerializerForThesis(allow_null=True, required=False)
    auxiliary_advisor = PersonSerializerForThesis(allow_null=True, required=False)
    student = PersonSerializerForThesis(allow_null=True, required=False)
    student_2 = PersonSerializerForThesis(allow_null=True, required=False)
    added_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=False)
    modified_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=False)

    def validate(self, data):
        # self.context will not be defined for local serialization
        # no special validation needs to be performed then (drf already provides
        # basic validation based on the constraints above)
        if not self.context:
            return data
        request = self.context["request"]
        if request.method == "POST":
            return self.validate_add_thesis(request.user, data)
        elif request.method == "PATCH":
            return self.validate_modify_thesis(request.user, data)
        else:
            raise serializers.ValidationError(f'Unknown request type {request.method}')

    def validate_add_thesis(user: User, data: dict):
        user_type = get_user_type(user)
        advisor = get_person(Employee, data["advisor"])
        if not can_set_advisor(user, user_type, advisor):
            raise serializers.ValidationError(f'This type of user cannot set advisor to {advisor}')
        status = data["status"]
        if not can_set_status(user_type, status):
            raise serializers.ValidationError(f'This type of user cannot set status to {status}')
        result = {
            "title": data["title"],
            "reserved": data["reserved"],
            "kind": data["kind"],
            "status": status,
        }
        copy_if_present(result, data, "description")
        copy_if_present(result, data, "auxiliary_advisor", lambda a: get_person(Employee, a))
        copy_if_present(result, data, "student", lambda s: get_person(Student, s))
        copy_if_present(result, data, "student_2", lambda s: get_person(Student, s))
        return result

    def create(self, validated_data):
        new_instance = Thesis(
            title=validated_data.get("title"),
            kind=validated_data.get("kind"),
            status=validated_data.get("status"),
            reserved=validated_data.get("reserved"),
            advisor=validated_data.get("advisor"),
            auxiliary_advisor=validated_data.get("auxiliary_advisor")
        )
        if "description" in validated_data:
            new_instance.description = validated_data.get("description")
        new_instance.save()
        return new_instance

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.kind = validated_data.get('kind', instance.kind)
        instance.reserved = validated_data.get('reserved', instance.reserved)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        ThesisSerializer._assign_advisors(instance, validated_data)
        ThesisSerializer._assign_students(instance, validated_data)
        instance.save()
        return instance

    @staticmethod
    def _assign_advisors(instance, validated_data):
        if "advisor" in validated_data:
            instance.advisor = _get_person_from_queryset(Employee, validated_data.get("advisor"))
        if "auxiliary_advisor" in validated_data:
            instance.auxiliary_advisor = _get_person_from_queryset(
                Employee, validated_data.get("auxiliary_advisor")
            )

    @staticmethod
    def _assign_students(instance, validated_data):
        if "student" in validated_data:
            instance.student = _get_person_from_queryset(Student, validated_data.get("student"))
        if "student_2" in validated_data:
            instance.student_2 = _get_person_from_queryset(Student, validated_data.get("student_2"))

    class Meta:
        model = Thesis
        read_only_fields = ('id', )
        fields = (
            'id', 'title', 'advisor', 'auxiliary_advisor',
            'kind', 'reserved', 'description', 'status',
            'student', 'student_2', 'added_date', 'modified_date',
        )


def get_person(queryset, person_data):
    try:
        return queryset.objects.get(pk=person_data.get("id"))
    except queryset.DoesNotExist:
        raise InvalidQueryError("Bad person ID specified")


class CurrentUserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: User):
        return {
            "id": instance.pk,
            "type": get_user_type(instance).value
        }
