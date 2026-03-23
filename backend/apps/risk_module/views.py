from rest_framework import response, views

from apps.risk_module.serializers import RiskCategorizationSerializer
from apps.risk_module.services import RiskCategorizationService


class RiskCategorizationView(views.APIView):
    def post(self, request):
        serializer = RiskCategorizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(RiskCategorizationService().classify(serializer.validated_data["symbol"]))
