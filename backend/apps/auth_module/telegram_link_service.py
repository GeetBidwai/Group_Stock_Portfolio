from __future__ import annotations

from datetime import timedelta
import secrets
from urllib.parse import quote

from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.auth_module.models import TelegramLinkSession, UserProfile
from apps.auth_module.serializers import RegisterSerializer, TelegramLinkSessionStatusSerializer
from apps.shared.services.telegram_notification_service import TelegramNotificationService


class TelegramSignupLinkService:
    def __init__(self):
        self.telegram_service = TelegramNotificationService()

    def create_session(self) -> dict:
        if not settings.TELEGRAM_BOT_USERNAME:
            raise ValidationError("Telegram bot username is not configured.")

        session = TelegramLinkSession.objects.create(
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(seconds=settings.TELEGRAM_SIGNUP_LINK_EXPIRY_SECONDS),
        )
        deep_link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={session.token}"
        return {
            "session_token": session.token,
            "status": session.status,
            "expires_at": session.expires_at,
            "deep_link": deep_link,
            "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=280x280&data={quote(deep_link, safe='')}",
        }

    def get_status(self, token: str) -> dict:
        session = self._get_session(token)
        if session.is_expired() and session.status not in (
            TelegramLinkSession.STATUS_CONSUMED,
            TelegramLinkSession.STATUS_EXPIRED,
        ):
            session.status = TelegramLinkSession.STATUS_EXPIRED
            session.save(update_fields=["status"])
        return TelegramLinkSessionStatusSerializer(session).data

    def handle_webhook_update(self, payload: dict) -> dict:
        message = (payload or {}).get("message") or {}
        text = (message.get("text") or "").strip()
        chat = message.get("chat") or {}
        from_user = message.get("from") or {}

        if not text.startswith("/start"):
            return {"processed": False}

        parts = text.split(maxsplit=1)
        token = parts[1].strip() if len(parts) > 1 else ""
        if not token:
            self._safe_send_message(chat.get("id"), "Open the signup QR link again to continue linking your account.")
            return {"processed": True, "linked": False}

        session = TelegramLinkSession.objects.filter(token=token).first()
        if not session:
            self._safe_send_message(chat.get("id"), "This signup link is invalid. Generate a fresh QR code in the app.")
            return {"processed": True, "linked": False}

        if session.is_expired():
            if session.status != TelegramLinkSession.STATUS_EXPIRED:
                session.status = TelegramLinkSession.STATUS_EXPIRED
                session.save(update_fields=["status"])
            self._safe_send_message(chat.get("id"), "This signup link has expired. Generate a new QR code in the app.")
            return {"processed": True, "linked": False}

        if session.status == TelegramLinkSession.STATUS_CONSUMED:
            self._safe_send_message(chat.get("id"), "This signup link has already been used.")
            return {"processed": True, "linked": False}

        if session.status == TelegramLinkSession.STATUS_LINKED and session.telegram_user_id not in (None, from_user.get("id")):
            self._safe_send_message(chat.get("id"), "This signup link is already linked to another Telegram account.")
            return {"processed": True, "linked": False}

        if UserProfile.objects.filter(telegram_chat_id=str(chat.get("id") or "")).exists():
            self._safe_send_message(chat.get("id"), "This Telegram account is already linked to an existing profile.")
            return {"processed": True, "linked": False}

        session.telegram_chat_id = str(chat.get("id") or "")
        session.telegram_username = (from_user.get("username") or "").strip()
        session.telegram_user_id = from_user.get("id")
        session.linked_at = timezone.now()
        session.status = TelegramLinkSession.STATUS_LINKED
        session.save(
            update_fields=[
                "telegram_chat_id",
                "telegram_username",
                "telegram_user_id",
                "linked_at",
                "status",
            ]
        )

        self._safe_send_message(chat.get("id"), "Telegram linked successfully. Return to the signup page to finish creating your account.")
        return {"processed": True, "linked": True}

    def complete_signup(self, payload: dict):
        session = self._get_session(payload["session_token"])

        if session.is_expired():
            if session.status != TelegramLinkSession.STATUS_EXPIRED:
                session.status = TelegramLinkSession.STATUS_EXPIRED
                session.save(update_fields=["status"])
            raise ValidationError("This Telegram signup link has expired. Please generate a new one.")

        if session.status == TelegramLinkSession.STATUS_CONSUMED:
            raise ValidationError("This Telegram signup link has already been used.")

        if session.status != TelegramLinkSession.STATUS_LINKED or not session.telegram_chat_id:
            raise ValidationError("Link your Telegram account before completing signup.")

        if UserProfile.objects.filter(telegram_chat_id=session.telegram_chat_id).exists():
            raise ValidationError("This Telegram account is already linked to another user.")

        serializer = RegisterSerializer(
            data={
                "username": payload["username"],
                "email": payload["email"],
                "password": payload["password"],
                "first_name": payload.get("first_name", ""),
                "last_name": payload.get("last_name", ""),
                "mobile_number": payload["mobile_number"],
                "telegram_chat_id": session.telegram_chat_id,
                "telegram_username": session.telegram_username,
            }
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        session.status = TelegramLinkSession.STATUS_CONSUMED
        session.consumed_at = timezone.now()
        session.save(update_fields=["status", "consumed_at"])
        return user

    def _get_session(self, token: str) -> TelegramLinkSession:
        session = TelegramLinkSession.objects.filter(token=token).first()
        if not session:
            raise ValidationError("Telegram signup link is invalid.")
        return session

    def _safe_send_message(self, chat_id, message: str) -> None:
        if not chat_id:
            return
        try:
            self.telegram_service.send_message(str(chat_id), message)
        except Exception:
            return
