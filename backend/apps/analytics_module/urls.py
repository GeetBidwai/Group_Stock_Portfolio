from django.urls import path

from apps.analytics_module.views import PortfolioPEComparisonView

urlpatterns = [path("pe-comparison", PortfolioPEComparisonView.as_view())]
