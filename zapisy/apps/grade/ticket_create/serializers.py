from rest_framework import serializers


class SigningRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True, min_value=0)
    ticket = serializers.IntegerField(required=True, min_value=0)


class SigningRequestsListSerializer(serializers.Serializer):
    signing_requests = serializers.ListField(child=SigningRequestSerializer())


class TicketSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    teacher = serializers.CharField(required=False)
    id = serializers.IntegerField(required=True, min_value=0)
    ticket = serializers.IntegerField(required=True, min_value=0)
    signature = serializers.IntegerField(required=True, min_value=0)


class TicketsListSerializer(serializers.Serializer):
    tickets = serializers.ListField(child=TicketSerializer())
