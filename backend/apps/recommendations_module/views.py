from rest_framework import response, views

from apps.recommendations_module.services.recommendation_service import RecommendationService


class RecommendationListView(views.APIView):
    def get(self, request):
        try:
            return response.Response(RecommendationService().generate_recommendations())
        except Exception:
            return response.Response({"error": "Unable to fetch recommendations"}, status=503)

