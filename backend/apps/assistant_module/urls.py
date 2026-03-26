from django.urls import path

from apps.assistant_module.views import PersonalAssistantChatView


urlpatterns = [
    path("chat/", PersonalAssistantChatView.as_view()),
]

