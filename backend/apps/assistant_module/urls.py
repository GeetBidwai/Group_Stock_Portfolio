from django.urls import path

from apps.assistant_module.views import PersonalAssistantChatView, PersonalAssistantReindexView


urlpatterns = [
    path("chat/", PersonalAssistantChatView.as_view()),
    path("reindex/", PersonalAssistantReindexView.as_view()),
]
