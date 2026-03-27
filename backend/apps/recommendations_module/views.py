import logging

from rest_framework import response, views

from apps.recommendations_module.services.recommendation_service import RecommendationService


logger = logging.getLogger(__name__)


class RecommendationListView(views.APIView):
    def get(self, request):
        try:
            return response.Response(RecommendationService().generate_recommendations())
        except Exception:
            logger.exception("Recommendations endpoint failed.")
            return response.Response({"error": "Unable to fetch recommendations"}, status=503)

