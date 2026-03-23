from rest_framework import generics, permissions, response, status, views
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.auth_module.models import UserSession
from apps.auth_module.serializers import (
    ForgotPasswordRequestSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    SessionSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)
from apps.auth_module.services import AuthService, PasswordResetService


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService().issue_tokens(serializer.validated_data["user"], request)
        return response.Response({"user": UserSerializer(serializer.validated_data["user"]).data, **tokens})


class RefreshView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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

    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(PasswordResetService().request_otp(serializer.validated_data["identifier"]))


class ForgotPasswordVerifyView(views.APIView):
    permission_classes = [permissions.AllowAny]

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

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetService().reset_password(
            serializer.validated_data["identifier"],
            serializer.validated_data["password"],
        )
        return response.Response({"message": "Password reset successful."})
