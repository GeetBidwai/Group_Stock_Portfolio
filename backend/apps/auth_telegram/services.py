from __future__ import annotations

import bcrypt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.auth_module.models import UserProfile
from apps.auth_module.serializers import UserSerializer
from apps.auth_module.services import AuthService
from apps.auth_telegram.models import TelegramAuthUser
from apps.auth_telegram.utils import verify_telegram_auth
from apps.shared.services.otp_service import OTPService
from apps.shared.services.telegram_notification_service import TelegramNotificationService

User = get_user_model()


class TelegramAuthService:
    RATE_LIMIT_ATTEMPTS = 5
    RATE_LIMIT_WINDOW_SECONDS = 60

    def __init__(self):
        self.telegram_service = TelegramNotificationService()

    @transaction.atomic
    def verify_telegram_login(self, payload: dict) -> dict:
        if not verify_telegram_auth(payload):
            raise ValidationError("Telegram authentication could not be verified.")

        telegram_id = int(payload["id"])
        username = (payload.get("username") or "").strip()
        telegram_user, _ = TelegramAuthUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={"username": username},
        )
        if username and telegram_user.username != username:
            telegram_user.username = username
            telegram_user.save(update_fields=["username"])

        return {
            "telegram_id": telegram_user.telegram_id,
            "username": telegram_user.username,
            "new_user": not bool(telegram_user.mpin_hash),
        }

    @transaction.atomic
    def set_mpin(self, telegram_id: int, mpin: str, request) -> dict:
        telegram_user = TelegramAuthUser.objects.filter(telegram_id=telegram_id).first()
        if not telegram_user:
            raise ValidationError("Telegram user not found. Please verify Telegram login first.")

        telegram_user.mpin_hash = bcrypt.hashpw(mpin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        if telegram_user.user is None:
            telegram_user.user = self._create_or_link_user(telegram_user)
        telegram_user.save(update_fields=["mpin_hash", "user"])

        tokens = AuthService().issue_tokens(telegram_user.user, request)
        return {
            "message": "MPIN set successfully.",
            "user": UserSerializer(telegram_user.user).data,
            **tokens,
        }

    def login_with_mpin(self, telegram_id: int, mpin: str, request) -> dict:
        telegram_user = (
            TelegramAuthUser.objects.select_related("user")
            .filter(telegram_id=telegram_id)
            .first()
        )
        if not telegram_user or not telegram_user.mpin_hash:
            raise ValidationError("MPIN has not been set for this Telegram account.")

        self._check_rate_limit(telegram_id)
        if not bcrypt.checkpw(mpin.encode("utf-8"), telegram_user.mpin_hash.encode("utf-8")):
            self._register_failed_attempt(telegram_id)
            raise ValidationError("Invalid MPIN.")

        self._clear_failed_attempts(telegram_id)
        if telegram_user.user is None:
            telegram_user.user = self._create_or_link_user(telegram_user)
            telegram_user.save(update_fields=["user"])

        tokens = AuthService().issue_tokens(telegram_user.user, request)
        return {
            "message": "Login successful.",
            "user": UserSerializer(telegram_user.user).data,
            **tokens,
        }

    def request_mobile_otp(self, phone_number: str) -> dict:
        normalized_phone = self._normalize_phone_number(phone_number)
        telegram_user = (
            TelegramAuthUser.objects.select_related("user__profile")
            .filter(phone_number=normalized_phone)
            .first()
        )
        if not telegram_user:
            raise ValidationError("No Telegram-linked account was found for this mobile number.")

        resend_key = self._otp_resend_key(normalized_phone)
        seconds_left = int(cache.get(resend_key, 0) or 0)
        if seconds_left > 0:
            raise ValidationError(f"OTP resend is on cooldown for {seconds_left} more seconds.")

        code = OTPService.generate_code()
        if telegram_user.user is None:
            telegram_user.user = self._create_or_link_user(telegram_user)
            telegram_user.save(update_fields=["user"])

        cache.set(
            self._otp_code_key(normalized_phone),
            OTPService.hash_code(code),
            settings.TELEGRAM_OTP_EXPIRY_SECONDS,
        )
        cache.set(
            resend_key,
            settings.TELEGRAM_OTP_RESEND_COOLDOWN_SECONDS,
            settings.TELEGRAM_OTP_RESEND_COOLDOWN_SECONDS,
        )
        minutes = max(1, settings.TELEGRAM_OTP_EXPIRY_SECONDS // 60)
        self.telegram_service.send_otp(
            str(telegram_user.telegram_id),
            f"Your stock analytics MPIN reset code is {code}. It expires in {minutes} minute(s).",
        )
        return {
            "phone_number": normalized_phone,
            "otp_required": True,
            "message": "OTP sent to your linked Telegram account.",
        }

    def verify_mobile_otp(self, phone_number: str, otp: str) -> dict:
        normalized_phone = self._normalize_phone_number(phone_number)
        telegram_user = (
            TelegramAuthUser.objects.select_related("user")
            .filter(phone_number=normalized_phone)
            .first()
        )
        if not telegram_user:
            raise ValidationError("No Telegram-linked account was found for this mobile number.")

        otp_hash = cache.get(self._otp_code_key(normalized_phone))
        if not otp_hash:
            raise ValidationError("OTP was not requested.")
        if otp_hash != OTPService.hash_code(otp):
            raise ValidationError("Invalid OTP.")

        cache.set(
            self._otp_verified_key(normalized_phone),
            {"telegram_id": telegram_user.telegram_id},
            settings.OTP_VERIFIED_CACHE_SECONDS,
        )
        cache.delete(self._otp_code_key(normalized_phone))
        return {
            "otp_verified": True,
            "reset_required": True,
            "telegram_id": telegram_user.telegram_id,
        }

    @transaction.atomic
    def reset_mpin_after_otp(self, telegram_id: int, new_mpin: str) -> dict:
        telegram_user = TelegramAuthUser.objects.select_related("user").filter(telegram_id=telegram_id).first()
        if not telegram_user:
            raise ValidationError("Telegram account not found.")
        normalized_phone = self._normalize_phone_number(telegram_user.phone_number)
        if not normalized_phone:
            raise ValidationError("A mobile number is not linked to this Telegram account.")
        cache_payload = cache.get(self._otp_verified_key(normalized_phone))
        if not cache_payload or int(cache_payload.get("telegram_id", 0)) != telegram_user.telegram_id:
            raise ValidationError("OTP verification is required before resetting MPIN.")

        telegram_user.mpin_hash = bcrypt.hashpw(new_mpin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        if telegram_user.user is None:
            telegram_user.user = self._create_or_link_user(telegram_user)
        telegram_user.save(update_fields=["mpin_hash", "user"])

        cache.delete(self._otp_verified_key(normalized_phone))
        cache.delete(self._otp_code_key(normalized_phone))
        cache.delete(self._otp_resend_key(normalized_phone))
        self._clear_failed_attempts(telegram_user.telegram_id)
        return {"message": "MPIN reset successful.", "telegram_id": telegram_user.telegram_id}

    def _create_or_link_user(self, telegram_user: TelegramAuthUser):
        base_username = (telegram_user.username or f"tg_{telegram_user.telegram_id}").strip()[:150] or f"tg_{telegram_user.telegram_id}"
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username[:140]}_{suffix}"
            suffix += 1

        email = f"telegram_{telegram_user.telegram_id}@telegram.local"
        while User.objects.filter(email=email).exists():
            email = f"telegram_{telegram_user.telegram_id}_{suffix}@telegram.local"
            suffix += 1

        user = User.objects.create(username=username, email=email)
        user.set_unusable_password()
        user.save(update_fields=["password"])
        UserProfile.objects.get_or_create(
            user=user,
            defaults={"telegram_username": telegram_user.username or ""},
        )
        return user

    def _normalize_phone_number(self, phone_number: str) -> str:
        digits = "".join(ch for ch in str(phone_number or "") if ch.isdigit())
        if len(digits) < 10:
            raise ValidationError("Enter a valid mobile number.")
        return digits

    def _otp_code_key(self, phone_number: str) -> str:
        return f"otp_code_{phone_number}"

    def _otp_resend_key(self, phone_number: str) -> str:
        return f"otp_resend_{phone_number}"

    def _otp_verified_key(self, phone_number: str) -> str:
        return f"otp_verified_{phone_number}"

    def _rate_limit_key(self, telegram_id: int) -> str:
        return f"telegram-auth:attempts:{telegram_id}"

    def _check_rate_limit(self, telegram_id: int) -> None:
        attempts = int(cache.get(self._rate_limit_key(telegram_id), 0))
        if attempts >= self.RATE_LIMIT_ATTEMPTS:
            raise ValidationError("Too many login attempts. Please wait a minute and try again.")

    def _register_failed_attempt(self, telegram_id: int) -> None:
        key = self._rate_limit_key(telegram_id)
        attempts = int(cache.get(key, 0)) + 1
        cache.set(key, attempts, self.RATE_LIMIT_WINDOW_SECONDS)

    def _clear_failed_attempts(self, telegram_id: int) -> None:
        cache.delete(self._rate_limit_key(telegram_id))
