from rest_framework import response, views

from apps.commodities_module.services import GoldSilverCorrelationService


class GoldSilverCorrelationView(views.APIView):
    def get(self, request):
        return response.Response(GoldSilverCorrelationService().analyze())
