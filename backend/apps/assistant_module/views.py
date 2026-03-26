from rest_framework import response, views

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

