from django.urls import path

from apps.sentiment_module.views import SentimentAnalyzeView, SentimentReportView


urlpatterns = [
    path("analyze/", SentimentAnalyzeView.as_view()),
    path("report/", SentimentReportView.as_view()),
]

