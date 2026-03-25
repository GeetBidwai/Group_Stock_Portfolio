from django.conf import settings
from django.db import models


class TelegramAuthUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=32, blank=True, db_index=True)
    mpin_hash = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="telegram_auth",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.telegram_id}"
