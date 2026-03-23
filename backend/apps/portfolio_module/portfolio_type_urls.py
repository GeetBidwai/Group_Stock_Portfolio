from django.urls import path

from apps.portfolio_module.views import PortfolioTypeDetailView, PortfolioTypeListCreateView

urlpatterns = [
    path("", PortfolioTypeListCreateView.as_view()),
    path("<int:pk>", PortfolioTypeDetailView.as_view()),
]
