from django.urls import path

from apps.auth_module import views

urlpatterns = [
    path("register", views.RegisterView.as_view()),
    path("signup", views.SignupView.as_view()),
    path("signup/", views.SignupView.as_view()),
    path("login", views.LoginView.as_view()),
    path("login/", views.LoginView.as_view()),
    path("refresh", views.RefreshView.as_view()),
    path("logout", views.LogoutView.as_view()),
    path("me", views.MeView.as_view()),
    path("sessions", views.SessionListView.as_view()),
]
