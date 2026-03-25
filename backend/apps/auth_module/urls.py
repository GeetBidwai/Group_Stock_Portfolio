from django.urls import path

from apps.auth_module import views

urlpatterns = [
    path("register", views.RegisterView.as_view()),
    path("signup/telegram-link/session", views.TelegramLinkSessionCreateView.as_view()),
    path("signup/telegram-link/status/<str:token>", views.TelegramLinkSessionStatusView.as_view()),
    path("signup/telegram-link/complete", views.TelegramLinkSignupCompleteView.as_view()),
    path("telegram/webhook", views.TelegramWebhookView.as_view()),
    path("login", views.LoginView.as_view()),
    path("refresh", views.RefreshView.as_view()),
    path("logout", views.LogoutView.as_view()),
    path("me", views.MeView.as_view()),
    path("sessions", views.SessionListView.as_view()),
    path("request-reset-otp", views.RequestResetOTPView.as_view()),
    path("verify-otp", views.VerifyResetOTPView.as_view()),
    path("reset-password", views.ResetPasswordWithTokenView.as_view()),
    path("forgot-password/request-otp", views.ForgotPasswordRequestView.as_view()),
    path("forgot-password/verify-otp", views.ForgotPasswordVerifyView.as_view()),
    path("forgot-password/reset-password", views.ForgotPasswordResetView.as_view()),
]
