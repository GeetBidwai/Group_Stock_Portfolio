from django.urls import path

from apps.recommendations_module.views import RecommendationListView


urlpatterns = [
    path("", RecommendationListView.as_view()),
]

