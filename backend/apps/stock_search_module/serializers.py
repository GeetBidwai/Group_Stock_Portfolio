from rest_framework import serializers

from apps.stock_search_module.models import StockReference


class StockSearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True, max_length=100)

    def validate_q(self, value: str) -> str:
        query = value.strip()
        if not query:
            raise serializers.ValidationError("Query parameter 'q' is required.")
        return query


class StockReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockReference
        fields = ("symbol", "name")
