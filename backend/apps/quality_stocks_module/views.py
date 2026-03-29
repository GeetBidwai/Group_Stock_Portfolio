from rest_framework import permissions, response, views

from apps.quality_stocks_module.models import QualityStock
from apps.quality_stocks_module.serializers import (
    QualityGenerateRequestSerializer,
    QualitySnapshotRequestSerializer,
    QualitySectorGenerateRequestSerializer,
    QualitySectorSnapshotRequestSerializer,
    QualityStockDetailSerializer,
    QualityStockListSerializer,
)
from apps.quality_stocks_module.services import QualityStocksService


class QualityStocksSnapshotView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QualitySnapshotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = QualityStocksService().snapshot(request.user, serializer.validated_data["portfolio_id"])
            return response.Response(payload)
        except Exception:
            return response.Response([])


class QualityStocksGenerateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QualityGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            items = QualityStocksService().generate_reports(
                request.user,
                serializer.validated_data["portfolio_id"],
                serializer.validated_data["stock_ids"],
            )
            return response.Response(QualityStockListSerializer(items, many=True).data)
        except Exception:
            return response.Response([])


class QualityStocksSectorSnapshotView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QualitySectorSnapshotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = QualityStocksService().sector_snapshot(request.user, serializer.validated_data["sector_name"])
            return response.Response(payload)
        except Exception:
            return response.Response([])


class QualityStocksSectorGenerateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QualitySectorGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            items = QualityStocksService().generate_sector_reports(
                request.user,
                serializer.validated_data["sector_name"],
                serializer.validated_data["stock_ids"],
            )
            return response.Response(QualityStockListSerializer(items, many=True).data)
        except Exception:
            return response.Response([])


class QualityStocksListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        portfolio_id = request.query_params.get("portfolio_id")
        queryset = QualityStock.objects.filter(user=request.user).select_related("portfolio", "stock").order_by("-generated_at")
        if portfolio_id:
            queryset = queryset.filter(portfolio_id=portfolio_id)
        return response.Response(QualityStockListSerializer(queryset, many=True).data)


class QualityStocksDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk: int) -> QualityStock | None:
        return QualityStock.objects.filter(user=request.user, pk=pk).select_related("portfolio", "stock").first()

    def get(self, request, pk: int):
        item = self.get_object(request, pk)
        if not item:
            return response.Response({"error": "Report not found"}, status=404)
        return response.Response(QualityStockDetailSerializer(item).data)

    def delete(self, request, pk: int):
        item = self.get_object(request, pk)
        if not item:
            return response.Response({"error": "Report not found"}, status=404)
        item.delete()
        return response.Response(status=204)


class QualityStocksRerunView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        item = QualityStock.objects.filter(user=request.user, pk=pk).select_related("portfolio", "stock").first()
        if not item:
            return response.Response({"error": "Report not found"}, status=404)
        try:
            report = QualityStocksService().rerun_report(request.user, item)
            return response.Response(QualityStockDetailSerializer(report).data)
        except Exception:
            return response.Response({"error": "Unable to rerun report"}, status=500)
