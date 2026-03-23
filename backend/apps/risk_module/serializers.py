from rest_framework import serializers


class RiskCategorizationSerializer(serializers.Serializer):
    symbol = serializers.CharField()
