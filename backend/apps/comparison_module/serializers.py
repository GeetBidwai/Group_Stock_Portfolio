from rest_framework import serializers


class StockComparisonSerializer(serializers.Serializer):
    primary_symbol = serializers.CharField()
    secondary_symbol = serializers.CharField()
