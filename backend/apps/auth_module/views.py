from rest_framework import generics, permissions, response, status, views
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import TokenError

from apps.auth_module.models import UserSession
from apps.auth_module.serializers import LoginSerializer, RegisterSerializer, SessionSerializer, UserSerializer
from apps.auth_module.services import AuthService


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = RegisterSerializer


class SignupView(RegisterView):
    pass


class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService().issue_tokens(serializer.validated_data["user"], request)
        return response.Response({"user": UserSerializer(serializer.validated_data["user"]).data, **tokens})


class RefreshView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise ValidationError({"refresh": [str(exc)]}) from exc
        return response.Response(serializer.validated_data)


class LogoutView(views.APIView):
    def post(self, request):
        refresh = request.data.get("refresh")
        if refresh:
            AuthService().revoke_session(refresh)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class MeView(views.APIView):
    def get(self, request):
        return response.Response(UserSerializer(request.user).data)


class SessionListView(generics.ListAPIView):
    serializer_class = SessionSerializer

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user, is_active=True).order_by("-last_seen_at")
