from django.urls import path

from apps.auth_telegram.views import (
    LoginMPINView,
    MobileOTPRequestView,
    MobileOTPVerifyView,
    ResetMPINAfterOTPView,
    SetMPINView,
    TelegramAuthView,
)

urlpatterns = [
    path("telegram/", TelegramAuthView.as_view()),
    path("set-mpin/", SetMPINView.as_view()),
    path("login-mpin/", LoginMPINView.as_view()),
    path("mobile/request-otp/", MobileOTPRequestView.as_view()),
    path("mobile/verify-otp/", MobileOTPVerifyView.as_view()),
    path("reset-mpin/", ResetMPINAfterOTPView.as_view()),
]
