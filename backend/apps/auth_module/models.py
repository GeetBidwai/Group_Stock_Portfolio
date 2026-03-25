from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    telegram_chat_id = models.BigIntegerField(blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=255, blank=True)
    telegram_username = models.CharField(max_length=255, blank=True)
    mobile_number = models.CharField(max_length=32, blank=True, db_index=True)


class TelegramLinkSession(models.Model):
    STATUS_PENDING = "pending"
    STATUS_LINKED = "linked"
    STATUS_CONSUMED = "consumed"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_LINKED, "Linked"),
        (STATUS_CONSUMED, "Consumed"),
        (STATUS_EXPIRED, "Expired"),
    )

    token = models.CharField(max_length=128, unique=True, db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    telegram_chat_id = models.CharField(max_length=255, blank=True)
    telegram_username = models.CharField(max_length=255, blank=True)
    telegram_user_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    linked_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, related_name="password_reset_otps", on_delete=models.CASCADE)
    otp_hash = models.CharField(max_length=255)
    failed_attempts = models.PositiveSmallIntegerField(default=0)
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
