from rest_framework import permissions, response, views

from apps.auth_telegram.serializers import (
    LoginMPINSerializer,
    MobileOTPRequestSerializer,
    MobileOTPVerifySerializer,
    ResetMPINSerializer,
    SetMPINSerializer,
    TelegramAuthSerializer,
)
from apps.auth_telegram.services import TelegramAuthService


class TelegramAuthView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TelegramAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = TelegramAuthService().verify_telegram_login(serializer.validated_data)
        return response.Response(payload)


class SetMPINView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SetMPINSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = TelegramAuthService().set_mpin(
            serializer.validated_data["telegram_id"],
            serializer.validated_data["mpin"],
            request,
        )
        return response.Response(payload)


class LoginMPINView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginMPINSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = TelegramAuthService().login_with_mpin(
            serializer.validated_data["telegram_id"],
            serializer.validated_data["mpin"],
            request,
        )
        return response.Response(payload)


class MobileOTPRequestView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MobileOTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = TelegramAuthService().request_mobile_otp(serializer.validated_data["phone_number"])
        return response.Response(payload)


class MobileOTPVerifyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MobileOTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = TelegramAuthService().verify_mobile_otp(
            serializer.validated_data["phone_number"],
            serializer.validated_data["otp"],
        )
        return response.Response(payload)


class ResetMPINAfterOTPView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetMPINSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = TelegramAuthService().reset_mpin_after_otp(
            serializer.validated_data["telegram_id"],
            serializer.validated_data["new_mpin"],
        )
        return response.Response(payload)
