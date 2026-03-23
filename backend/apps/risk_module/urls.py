from django.urls import path

from apps.risk_module.views import RiskCategorizationView

urlpatterns = [path("risk-categorization", RiskCategorizationView.as_view())]
