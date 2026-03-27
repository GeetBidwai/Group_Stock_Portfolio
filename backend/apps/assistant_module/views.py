from rest_framework import permissions, response, views

from apps.assistant_module.intent_detection import IntentDetectionService
from apps.assistant_module.rag.rag_pipeline import get_assistant_rag_pipeline
from apps.assistant_module.services import PersonalAssistantService


class PersonalAssistantChatView(views.APIView):
    def post(self, request):
        message = str(request.data.get("message") or "").strip()
        history = request.data.get("history") or []

        if not message:
            return response.Response({"error": "message is required"}, status=400)

        if not isinstance(history, list):
            return response.Response({"error": "history must be a list"}, status=400)

        result = PersonalAssistantService().reply(
            user=request.user,
            message=message,
            history=history,
        )
        return response.Response(result)


class DetectIntentView(views.APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        message = str(request.data.get("message") or "").strip()
        if not message:
            return response.Response({"error": "message is required"}, status=400)

        result = IntentDetectionService().detect(message)
        return response.Response(result)


class PersonalAssistantReindexView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request):
        result = get_assistant_rag_pipeline().reindex()
        status_code = 200 if result.get("ok") else 503
        return response.Response(result, status=status_code)
