from rest_framework import response, views

from apps.clustering_module.services import PortfolioClusteringService


class PortfolioClusteringView(views.APIView):
    def get(self, request):
        return response.Response(PortfolioClusteringService().cluster(request.user))

    def post(self, request):
        return self.get(request)
