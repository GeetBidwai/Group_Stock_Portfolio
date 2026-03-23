from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=255, blank=True)
    telegram_username = models.CharField(max_length=255, blank=True)


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, related_name="password_reset_otps", on_delete=models.CASCADE)
    otp_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    resend_available_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at


class UserSession(models.Model):
    user = models.ForeignKey(User, related_name="sessions", on_delete=models.CASCADE)
    refresh_token_jti = models.CharField(max_length=255, unique=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
