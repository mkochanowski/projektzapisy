from rest_framework import serializers


class SigningRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True, min_value=0)
    ticket = serializers.IntegerField(required=True)

class SigningRequestsListSerializer(serializers.Serializer):
    signing_requests = serializers.ListField(child=SigningRequestSerializer())