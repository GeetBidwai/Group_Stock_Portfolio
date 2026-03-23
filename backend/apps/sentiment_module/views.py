from django.http import HttpResponse
from rest_framework import response, views

from apps.sentiment_module.serializers import SentimentAnalyzeSerializer, SentimentReportSerializer
from apps.sentiment_module.services.report_service import SentimentReportService
from apps.sentiment_module.services.sentiment_service import SentimentAggregationService


class SentimentAnalyzeView(views.APIView):
    def post(self, request):
        serializer = SentimentAnalyzeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = SentimentAggregationService().analyze_stock(serializer.validated_data["stock"])
        status_code = result.pop("error_status", 200)
        return response.Response(result, status=status_code)


class SentimentReportView(views.APIView):
    def get(self, request):
        serializer = SentimentReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        try:
            pdf_bytes, filename = SentimentReportService().build_pdf(serializer.validated_data["stock"])
        except ValueError as exc:
            return response.Response({"error": str(exc)}, status=400)
        except Exception as exc:
            return response.Response({"error": str(exc)}, status=500)

        http_response = HttpResponse(pdf_bytes, content_type="application/pdf")
        http_response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return http_response

