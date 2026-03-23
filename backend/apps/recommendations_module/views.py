from rest_framework import response, views

from apps.recommendations_module.services.recommendation_service import RecommendationService


class RecommendationListView(views.APIView):
    def get(self, request):
        return response.Response(RecommendationService().generate_recommendations())

