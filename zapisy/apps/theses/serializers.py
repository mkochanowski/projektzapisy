"""Defines all (de)serialization logic related
to objects used in the theses system, that is:
* packing/unpacking logic
* validation
* fine-grained permissions checks
* performing modifications/adding new objects
"""
from typing import Dict, Any

from rest_framework import serializers

from apps.users.models import Employee, Student, BaseUser
from .models import Thesis, ThesisStatus, ThesisVote
from .users import wrap_user, get_user_type, is_theses_board_member
from .permissions import (
    can_set_status, can_set_advisor,
    can_cast_vote_as_user, can_change_status, can_change_title
)


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


def serialize_thesis_votes(thesis: Thesis):
    """Serializes the votes of the given thesis into a dict"""
    vote_tpls = (
        (vote.voter.pk, vote.value)
        for vote in thesis.votes.all()
        if vote.value != ThesisVote.none.value
    )
    return dict(vote_tpls)


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


def validate_advisor(user: BaseUser, advisor: Employee):
    """Check that the current user is permitted to set the specified advisor"""
    if not can_set_advisor(user, advisor):
        raise serializers.ValidationError(f'This type of user cannot set advisor to {advisor}')


def validate_thesis_vote(value):
    """Check if the given vote value is valid"""
    return value in [vote.value for vote in ThesisVote]


def validate_votes(votes, user: BaseUser):
    """Validate the votes dict for a thesis"""
    if type(votes) is not dict:
        raise serializers.ValidationError("\"votes\" must be an object")
    result = []
    for key, value in votes.items():
        if not validate_thesis_vote(value):
            raise serializers.ValidationError("invalid thesis vote value")
        try:
            voter_id = int(key)
            voter = Employee.objects.get(pk=voter_id)
            if not is_theses_board_member(voter):
                raise serializers.ValidationError("voter is not a member of the theses board")
            if not can_cast_vote_as_user(user, voter):
                raise serializers.ValidationError("this user cannot change that user's vote")
            result.append((voter, ThesisVote(value)))
        except (ValueError, Employee.DoesNotExist):
            raise serializers.ValidationError("bad voter id")
    return result


def handle_optional_fields(result, data, user: BaseUser):
    """Extract optional fields from the source dictionary (sent by the client),
    perform any necessary conversions, then place it in the result dictionary
    """
    copy_if_present(result, data, "description")
    copy_if_present(result, data, "votes", lambda votes: validate_votes(votes, user))
    copy_if_present(result, data, "auxiliary_advisor", lambda a: get_person(Employee, a))
    copy_if_present(result, data, "student", lambda s: get_person(Student, s))
    copy_if_present(result, data, "student_2", lambda s: get_person(Student, s))


class ThesisSerializer(serializers.ModelSerializer):
    advisor = PersonSerializerForThesis(allow_null=True, required=False)
    auxiliary_advisor = PersonSerializerForThesis(allow_null=True, required=False)
    student = PersonSerializerForThesis(allow_null=True, required=False)
    student_2 = PersonSerializerForThesis(allow_null=True, required=False)
    added_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=False)
    modified_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=False)
    votes = serializers.SerializerMethodField()

    def to_internal_value(self, data):
        result = super().to_internal_value(data)
        if "votes" in data:
            result["votes"] = data["votes"]
        return result

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
        wrapped_user = wrap_user(request.user)
        if request.method == "POST":
            return self.validate_add_thesis(wrapped_user, data)
        elif request.method == "PATCH":
            return self.validate_modify_thesis(wrapped_user, data)
        else:
            raise serializers.ValidationError(f'Unknown request type {request.method}')

    def validate_add_thesis(self, user: BaseUser, data: ValidationData):
        """Validate a request to add a new thesis object; basic permissions
        checks have already been performed, so this deals with more detailed checks
        (is the given status valid for this type of user) and conversions
        """
        advisor = get_person(Employee, data["advisor"]) if "advisor" in data else None
        validate_advisor(user, advisor)
        status = data["status"]
        if not can_set_status(user, ThesisStatus(status)):
            raise serializers.ValidationError(f'This type of user cannot set status to {status}')
        result = {
            "title": data["title"],
            "reserved": data["reserved"],
            "kind": data["kind"],
            "status": status,
            "advisor": advisor,
        }
        handle_optional_fields(result, data, user)
        if "description" not in result:
            result["description"] = ""

        return result

    def validate_modify_thesis(self, user: BaseUser, data: ValidationData):
        """As above, but this time the thesis object already exists. There is some
        additional logic in this case; for instance, if a thesis is already accepted,
        its owner/advisor cannot change the title anymore
        """
        result = {}
        if "advisor" in data:
            advisor = get_person(Employee, data["advisor"])
            validate_advisor(user, advisor)
            result["advisor"] = advisor
        if "status" in data:
            if not can_change_status(user):
                raise serializers.ValidationError("This type of user cannot modify the status")
            result["status"] = data["status"]
        if "title" in data:
            title = data["title"]
            if not can_change_title(user, self.instance):
                raise serializers.ValidationError("This type of user cannot change the title")
            result["title"] = title
        copy_if_present(result, data, "reserved")
        copy_if_present(result, data, "kind")
        handle_optional_fields(result, data, user)

        return result

    def create(self, validated_data):
        """If the checks above succeed, DRF will call this method
        in response to a POST request with the dictionary we returned
        from validate_add_thesis
        """
        new_instance = Thesis.objects.create(
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
        if "votes" in validated_data:
            new_instance.process_new_votes(validated_data["votes"])
        return new_instance

    def update(self, instance, validated_data):
        """As above"""
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
        if "votes" in validated_data:
            instance.process_new_votes(validated_data["votes"])
        return instance

    def get_votes(self, instance):
        return serialize_thesis_votes(instance)

    class Meta:
        model = Thesis
        read_only_fields = ('id', )
        fields = (
            'id', 'title', 'advisor', 'auxiliary_advisor',
            'kind', 'reserved', 'description', 'status',
            'student', 'student_2', 'added_date', 'modified_date',
            'votes',
        )


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
