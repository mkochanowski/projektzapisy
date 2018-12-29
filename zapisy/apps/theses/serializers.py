"""Defines all (de)serialization logic related
to objects used in the theses system, that is:
* packing/unpacking logic
* validation
* fine-grained permissions checks
* performing modifications/adding new objects
"""
from typing import Dict, Any, Optional

from rest_framework import serializers, exceptions

from apps.users.models import Employee, Student, BaseUser
from .models import Thesis, ThesisStatus, MAX_THESIS_TITLE_LEN
from .users import wrap_user, get_user_type
from .permissions import can_set_status, can_set_advisor, can_change_status, can_change_title
from .drf_errors import ThesisNameConflict


class PersonSerializerForThesis(serializers.Serializer):
    """Used to serialize user profiles as needed by various parts of the system;
    we don't want to use the user serializer from apps.api.rest
    because it packs too much data, and size matters here as we'll send it
    for every thesis
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


ValidationData = Dict[str, Any]


def get_person(queryset, person_data):
    """Given a person object of the format specified above (in PersonSerializer.to_internal_value)
    and a queryset, try to return the corresponding model instance
    """
    try:
        return queryset.objects.get(pk=person_data.get("id")) if person_data else None
    except queryset.DoesNotExist:
        raise serializers.ValidationError("bad person ID specified")


def copy_if_present(dst, src, key, converter=None):
    """If the given key is present in the source dictionary,
    copy it to the destination dictionary optionally applying the
    supplied conversion function if present
    """
    if key in src:
        dst[key] = converter(src[key]) if converter else src[key]


def copy_optional_fields(result, data):
    """Extract optional fields from the source dictionary (sent by the client),
    perform any necessary conversions, then place it in the result dictionary
    """
    copy_if_present(result, data, "description")
    copy_if_present(result, data, "auxiliary_advisor", lambda a: get_person(Employee, a))
    copy_if_present(result, data, "student", lambda s: get_person(Student, s))
    copy_if_present(result, data, "student_2", lambda s: get_person(Student, s))


def validate_new_title_for_instance(title: str, instance: Optional[Thesis]):
    qs = Thesis.objects.filter(title=title.strip())
    if instance:
        qs = qs.exclude(pk=instance.pk)
    if qs.count():
        raise ThesisNameConflict()


def check_advisor_permissions(user: BaseUser, advisor: Employee):
    """Check that the current user is permitted to set the specified advisor"""
    if not can_set_advisor(user, advisor):
        raise exceptions.PermissionDenied(f'This type of user cannot set advisor to {advisor}')


class ThesisSerializer(serializers.ModelSerializer):
    advisor = PersonSerializerForThesis(allow_null=True, required=False)
    auxiliary_advisor = PersonSerializerForThesis(allow_null=True, required=False)
    student = PersonSerializerForThesis(allow_null=True, required=False)
    student_2 = PersonSerializerForThesis(allow_null=True, required=False)
    added_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=False)
    modified_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=False)

    # We need to define this field here manually to disable DRF's unique validator which
    # isn't flexible enough to override the error code it returns (throws a 400, we want 409)
    # See https://stackoverflow.com/q/33475334
    # and https://github.com/encode/django-rest-framework/issues/6124
    title = serializers.CharField(max_length=MAX_THESIS_TITLE_LEN)

    def validate(self, data):
        """Validate a dict object received from the frontend client;
        DRF expects us to return a dict object to be used for further processing,
        so we use this opportunity to perform conversions to more convenient formats
        """
        # self.context will not be defined for local serialization
        # presently we don't use this serializer in a local context, and even if we did,
        # no special validation needs to be performed then (drf already provides
        # basic validation based on the constraints above)
        if not self.context:
            return data
        request = self.context["request"]
        if request.method == "POST":
            return self.validate_add_thesis(data)
        elif request.method == "PATCH":
            return self.validate_modify_thesis(data)
        else:
            raise serializers.ValidationError(f'Unknown request type {request.method}')

    def validate_add_thesis(self, data: ValidationData):
        """Validate a request to add a new thesis object and convert to more convenient
        local types
        """
        advisor = get_person(Employee, data["advisor"]) if "advisor" in data else None
        validate_new_title_for_instance(data["title"], None)
        result = {
            "title": data["title"],
            "reserved": data["reserved"],
            "kind": data["kind"],
            "status": data["status"],
            "advisor": advisor,
        }
        copy_optional_fields(result, data)
        if "description" not in result:
            result["description"] = ""

        return result

    def validate_modify_thesis(self, data: ValidationData):
        """As above, but this time the thesis object already exists. There is some
        additional logic in this case; for instance, if a thesis is already accepted,
        its owner/advisor cannot change the title anymore
        """
        if "title" in data:
            validate_new_title_for_instance(data["title"], self.instance)
        result = {}
        copy_if_present(result, data, "advisor", lambda a: get_person(Employee, a))
        copy_if_present(result, data, "status")
        copy_if_present(result, data, "title")
        copy_if_present(result, data, "reserved")
        copy_if_present(result, data, "kind")
        copy_optional_fields(result, data)

        return result

    def create(self, validated_data):
        """If the checks above succeed, DRF will call this method
        in response to a POST request with the dictionary we returned
        from validate_add_thesis
        """
        # First check that the user is permitted to set these values
        request = self.context["request"]
        user = wrap_user(request.user)
        check_advisor_permissions(user, validated_data["advisor"])
        status = validated_data["status"]
        if not can_set_status(user, ThesisStatus(status)):
            raise exceptions.PermissionDenied(f'This type of user cannot set status to {status}')

        return Thesis.objects.create(
            title=validated_data.get("title"),
            kind=validated_data.get("kind"),
            status=validated_data.get("status"),
            reserved=validated_data.get("reserved"),
            description=validated_data.get("description"),
            advisor=validated_data.get("advisor"),
            auxiliary_advisor=validated_data.get("auxiliary_advisor"),
            student=validated_data.get("student"),
            student_2=validated_data.get("student_2"),
        )

    def update(self, instance, validated_data):
        """Called in response to a successfully validated PATCH request"""
        request = self.context["request"]
        user = wrap_user(request.user)
        if "advisor" in validated_data:
            check_advisor_permissions(user, validated_data["advisor"])
        if "status" in validated_data:
            if not can_change_status(user):
                raise exceptions.PermissionDenied("This type of user cannot modify the status")
        if "title" in validated_data:
            if not can_change_title(user, self.instance):
                raise exceptions.PermissionDenied("This type of user cannot change the title")

        instance.title = validated_data.get("title", instance.title)
        instance.kind = validated_data.get("kind", instance.kind)
        instance.reserved = validated_data.get("reserved", instance.reserved)
        instance.description = validated_data.get("description", instance.description)
        instance.status = validated_data.get("status", instance.status)
        instance.advisor = validated_data.get("advisor", instance.advisor)
        instance.auxiliary_advisor = validated_data.get(
            "auxiliary_advisor", instance.auxiliary_advisor
        )
        instance.student = validated_data.get("student", instance.student)
        instance.student_2 = validated_data.get("student_2", instance.student_2)
        instance.save()
        return instance

    class Meta:
        model = Thesis
        read_only_fields = ('id', )
        fields = (
            'id', 'title', 'advisor', 'auxiliary_advisor',
            'kind', 'reserved', 'description', 'status',
            'student', 'student_2', 'added_date', 'modified_date',
        )
        extra_kwargs = {
            "title": {"error_messages": {"unique": "Give yourself a username"}}
        }


class CurrentUserSerializer(serializers.ModelSerializer):
    """Serialize the currently logged in user; this also needs to send the user type,
    so it's a separate serializer"""
    def to_representation(self, instance: BaseUser):
        return {
            "user": PersonSerializerForThesis(instance).data,
            "type": get_user_type(instance).value
        }


class ThesesBoardMemberSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: Employee):
        return {
            "id": instance.id,
            "display_name": instance.user.username,
        }
