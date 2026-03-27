from django.urls import path

from apps.assistant_module.views import DetectIntentView, PersonalAssistantChatView, PersonalAssistantReindexView


urlpatterns = [
    path("detect-intent/", DetectIntentView.as_view()),
    path("chat/", PersonalAssistantChatView.as_view()),
    path("reindex/", PersonalAssistantReindexView.as_view()),
]
