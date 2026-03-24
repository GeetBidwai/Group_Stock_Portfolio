from rest_framework import response, views

from apps.analytics_module.services import PortfolioPEComparisonService, PortfolioStockAnalyticsService, StockAnalyticsService


class StockAnalyticsView(views.APIView):
    def get(self, request, symbol: str):
        return response.Response(StockAnalyticsService().get_stock_analytics(symbol))


class PortfolioPEComparisonView(views.APIView):
    def get(self, request):
        return response.Response(PortfolioPEComparisonService().compare_for_user(request.user))


class PortfolioStockAnalyticsView(views.APIView):
    def get(self, request):
        portfolio_type_id = request.query_params.get("portfolio_id")
        if not portfolio_type_id:
            return response.Response({"error": "portfolio_id is required"}, status=400)

        try:
            normalized_portfolio_id = int(portfolio_type_id)
        except (TypeError, ValueError):
            return response.Response({"error": "portfolio_id must be a number"}, status=400)

        return response.Response(
            PortfolioStockAnalyticsService().summarize_portfolio(request.user, normalized_portfolio_id)
        )
