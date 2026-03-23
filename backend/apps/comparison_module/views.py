from rest_framework import response, views

from apps.comparison_module.serializers import StockComparisonSerializer
from apps.comparison_module.services import StockComparisonService


class StockComparisonView(views.APIView):
    def post(self, request):
        serializer = StockComparisonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return response.Response(StockComparisonService().compare(data["primary_symbol"], data["secondary_symbol"]))
