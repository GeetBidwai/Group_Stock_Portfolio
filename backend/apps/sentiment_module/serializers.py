from rest_framework import serializers


class SentimentAnalyzeSerializer(serializers.Serializer):
    stock = serializers.CharField()


class SentimentReportSerializer(serializers.Serializer):
    stock = serializers.CharField()

