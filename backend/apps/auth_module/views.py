from django.conf import settings
from rest_framework import generics, permissions, response, status, views
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import TokenError

from apps.auth_module.models import UserSession
from apps.auth_module.serializers import (
    ForgotPasswordRequestSerializer,
    LoginSerializer,
    CompleteTelegramSignupSerializer,
    RequestResetOTPSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    ResetPasswordWithTokenSerializer,
    SessionSerializer,
    TelegramLinkSessionCreateSerializer,
    UserSerializer,
    VerifyOTPSerializer,
    VerifyResetOTPSerializer,
)
from apps.auth_module.services import AuthService, PasswordResetService
from apps.auth_module.telegram_link_service import TelegramSignupLinkService


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


class ForgotPasswordRequestView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(PasswordResetService().request_otp(serializer.validated_data["identifier"]))


class ForgotPasswordVerifyView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(
            PasswordResetService().verify_otp(
                serializer.validated_data["identifier"],
                serializer.validated_data["otp"],
            )
        )


class ForgotPasswordResetView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetService().reset_password(
            serializer.validated_data["identifier"],
            serializer.validated_data["password"],
        )
        return response.Response({"message": "Password reset successful."})


class RequestResetOTPView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RequestResetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(
            PasswordResetService().request_reset_otp(
                serializer.validated_data["phone_number"],
                serializer.validated_data.get("telegram_chat_id"),
            )
        )


class VerifyResetOTPView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = VerifyResetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(
            PasswordResetService().verify_reset_otp(
                serializer.validated_data["phone_number"],
                serializer.validated_data["otp_code"],
            )
        )


class ResetPasswordWithTokenView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordWithTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get("token"):
            PasswordResetService().reset_password_with_token(
                serializer.validated_data["token"],
                serializer.validated_data["new_password"],
            )
        else:
            PasswordResetService().reset_password_by_mobile(
                serializer.validated_data["phone_number"],
                serializer.validated_data["new_password"],
            )
        return response.Response({"message": "Password reset successful."})


class TelegramLinkSessionCreateView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = TelegramLinkSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(TelegramSignupLinkService().create_session(), status=status.HTTP_201_CREATED)


class TelegramLinkSessionStatusView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request, token: str):
        return response.Response(TelegramSignupLinkService().get_status(token))


class TelegramLinkSignupCompleteView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = CompleteTelegramSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = TelegramSignupLinkService().complete_signup(serializer.validated_data)
        return response.Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class TelegramWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        expected_secret = (getattr(request, "_request", request).META.get("HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN") or "").strip()
        configured_secret = (settings.TELEGRAM_WEBHOOK_SECRET or "").strip()
        if configured_secret and expected_secret != configured_secret:
            return response.Response({"detail": "Invalid webhook secret."}, status=status.HTTP_403_FORBIDDEN)
        payload = TelegramSignupLinkService().handle_webhook_update(request.data)
        return response.Response(payload, status=status.HTTP_200_OK)
