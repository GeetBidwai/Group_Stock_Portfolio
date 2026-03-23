from rest_framework import response, views

from apps.commodities_module.commodity_service import CommodityAnalyticsService


class GoldView(views.APIView):
    def get(self, request):
        try:
            return response.Response(CommodityAnalyticsService().build_gold_payload())
        except Exception:
            return response.Response({"error": "Data unavailable"})


class SilverView(views.APIView):
    def get(self, request):
        try:
            return response.Response(CommodityAnalyticsService().build_silver_payload())
        except Exception:
            return response.Response({"error": "Data unavailable"})


class CorrelationView(views.APIView):
    def get(self, request):
        try:
            return response.Response(CommodityAnalyticsService().build_correlation_payload())
        except Exception:
            return response.Response({"error": "Data unavailable"})

