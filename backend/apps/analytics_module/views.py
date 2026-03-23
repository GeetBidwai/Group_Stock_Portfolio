from rest_framework import response, views

from apps.analytics_module.services import PortfolioPEComparisonService, StockAnalyticsService


class StockAnalyticsView(views.APIView):
    def get(self, request, symbol: str):
        return response.Response(StockAnalyticsService().get_stock_analytics(symbol))


class PortfolioPEComparisonView(views.APIView):
    def get(self, request):
        return response.Response(PortfolioPEComparisonService().compare_for_user(request.user))
