from rest_framework import response, views

from apps.comparison_module.serializers import StockComparisonSerializer
from apps.comparison_module.services import StockComparisonService
from apps.portfolio_module.models import PortfolioStock
from apps.stocks_module.models import PortfolioEntry


class StockComparisonView(views.APIView):
    def get(self, request):
        stock_a = request.query_params.get("stockA")
        stock_b = request.query_params.get("stockB")
        range_key = request.query_params.get("range", "6m")
        if not stock_a or not stock_b:
            return response.Response({"error": "stockA and stockB are required."}, status=400)

        try:
            result = StockComparisonService().compare_portfolio_stocks(request.user, stock_a, stock_b, range_key)
            return response.Response(result)
        except ValueError as exc:
            return response.Response({"error": str(exc)}, status=400)
        except Exception:
            return response.Response({"error": "Comparison data unavailable."}, status=503)

    def post(self, request):
        serializer = StockComparisonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return response.Response(StockComparisonService().compare(data["primary_symbol"], data["secondary_symbol"]))


class PortfolioStockOptionsView(views.APIView):
    def get(self, request):
        manual_portfolio_stocks = (
            PortfolioStock.objects.filter(user=request.user)
            .order_by("symbol", "company_name")
            .values("symbol", "company_name")
        )
        grouped_portfolio_stocks = (
            PortfolioEntry.objects.filter(user=request.user)
            .select_related("stock")
            .order_by("stock__symbol", "stock__name")
            .values("stock__symbol", "stock__name")
        )

        deduped = []
        seen = set()
        for stock in manual_portfolio_stocks:
            symbol = stock["symbol"].upper()
            if symbol in seen:
                continue
            seen.add(symbol)
            deduped.append({
                "symbol": symbol,
                "name": stock["company_name"] or symbol,
            })
        for stock in grouped_portfolio_stocks:
            symbol = stock["stock__symbol"].upper()
            if symbol in seen:
                continue
            seen.add(symbol)
            deduped.append({
                "symbol": symbol,
                "name": stock["stock__name"] or symbol,
            })
        return response.Response(deduped)
