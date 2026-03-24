from rest_framework import response, views

from apps.clustering_module.stock_clustering_service import StockClusteringService


class StockClusteringView(views.APIView):
    def get(self, request):
        method = request.query_params.get("method", "pca")
        k = request.query_params.get("k", 3)
        portfolio_id = request.query_params.get("portfolio_id")

        try:
            normalized_k = int(k)
        except (TypeError, ValueError):
            normalized_k = 3

        try:
            normalized_portfolio_id = int(portfolio_id) if portfolio_id else None
        except (TypeError, ValueError):
            normalized_portfolio_id = None

        result = StockClusteringService().cluster(
            request.user,
            method=method,
            k=normalized_k,
            portfolio_id=normalized_portfolio_id,
        )
        return response.Response(result)
