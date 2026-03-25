from datetime import timedelta
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q
from requests import RequestException
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.auth_module.models import PasswordResetOTP, UserSession
from apps.shared.services.otp_service import OTPService
from apps.shared.services.telegram_notification_service import TelegramNotificationService

User = get_user_model()


def send_telegram_message(chat_id, message: str) -> None:
    TelegramNotificationService().send_message(str(chat_id), message)


class AuthService:
    def issue_tokens(self, user, request) -> dict:
        refresh = RefreshToken.for_user(user)
        UserSession.objects.create(
            user=user,
            refresh_token_jti=str(refresh["jti"]),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
            ip_address=self._get_client_ip(request),
        )
        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    def revoke_session(self, refresh_token: str) -> None:
        token = RefreshToken(refresh_token)
        jti = str(token["jti"])
        UserSession.objects.filter(refresh_token_jti=jti).update(is_active=False)
        token.blacklist()

    def _get_client_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class PasswordResetService:
    REQUEST_LIMIT_WINDOW_SECONDS = 3600

    def __init__(self):
        self.telegram_service = TelegramNotificationService()

    def request_otp(self, identifier: str) -> dict:
        user = self._find_user(identifier)
        if not settings.AUTH_RESET_REQUIRE_OTP:
            otp = PasswordResetOTP.objects.create(
                user=user,
                otp_hash="dev-no-otp",
                expires_at=OTPService.get_expiry(),
                resend_available_at=timezone.now(),
                is_verified=True,
                verified_at=timezone.now(),
            )
            return {
                "identifier": identifier,
                "expires_at": otp.expires_at,
                "otp_required": False,
                "message": "OTP verification is disabled in this environment. You can reset the password directly.",
            }
        otp, delivery_payload = self._create_and_send_otp(user)
        return {"identifier": identifier, "expires_at": otp.expires_at, "otp_required": True, **delivery_payload}

    def request_reset_otp(self, mobile_number: str, telegram_chat_id: int | None = None) -> dict:
        user = self._find_user_by_mobile(mobile_number)
        if telegram_chat_id is not None:
            stored_chat_id = self._get_user_telegram_chat_id(user)
            if stored_chat_id != str(telegram_chat_id):
                raise ValidationError("Phone number and Telegram Chat ID do not match our records.")
        otp, delivery_payload = self._create_and_send_otp(user)
        return {
            "mobile_number": self._get_user_phone_number(user),
            "phone_number": self._get_user_phone_number(user),
            "telegram_chat_id": self._get_user_telegram_chat_id(user),
            "expires_at": otp.expires_at,
            **delivery_payload,
        }

    def verify_otp(self, identifier: str, otp: str) -> dict:
        if not settings.AUTH_RESET_REQUIRE_OTP:
            return {"verified": True, "otp_required": False}
        user = self._find_user(identifier)
        self._verify_otp_record(user, otp)
        return {"verified": True}

    def verify_reset_otp(self, mobile_number: str, otp: str) -> dict:
        user = self._find_user_by_mobile(mobile_number)
        self._verify_otp_record(user, otp)
        token = secrets.token_urlsafe(32)
        cache.set(self._reset_token_key(token), user.pk, settings.PASSWORD_RESET_TOKEN_EXPIRY_SECONDS)
        cache.set(
            self._otp_verified_key(self._get_user_phone_number(user)),
            {"user_id": user.pk},
            settings.PASSWORD_RESET_TOKEN_EXPIRY_SECONDS,
        )
        return {
            "verified": True,
            "token": token,
            "expires_in": settings.PASSWORD_RESET_TOKEN_EXPIRY_SECONDS,
        }

    def reset_password(self, identifier: str, password: str) -> None:
        user = self._find_user(identifier)
        record = PasswordResetOTP.objects.filter(user=user, is_verified=True, is_used=False).order_by("-created_at").first()
        if not record:
            raise ValidationError("OTP verification is required.")
        if record.is_expired():
            raise ValidationError("Verified OTP has expired.")
        user.set_password(password)
        user.save(update_fields=["password"])
        record.is_used = True
        record.save(update_fields=["is_used"])

    def reset_password_with_token(self, token: str, new_password: str) -> None:
        user_id = cache.get(self._reset_token_key(token))
        if not user_id:
            raise ValidationError("Reset token is invalid or has expired.")

        user = User.objects.filter(pk=user_id).first()
        if not user:
            cache.delete(self._reset_token_key(token))
            raise ValidationError("User not found for this reset token.")

        user.set_password(new_password)
        user.save(update_fields=["password"])
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
        cache.delete(self._reset_token_key(token))
        cache.delete(self._otp_verified_key(self._get_user_phone_number(user)))

    def reset_password_by_mobile(self, mobile_number: str, new_password: str) -> None:
        user = self._find_user_by_mobile(mobile_number)
        normalized_mobile_number = self._get_user_phone_number(user)
        verification_cache = cache.get(self._otp_verified_key(normalized_mobile_number))
        if not verification_cache or int(verification_cache.get("user_id", 0)) != user.pk:
            raise ValidationError("OTP verification is required before resetting the password.")

        user.set_password(new_password)
        user.save(update_fields=["password"])
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
        cache.delete(self._otp_verified_key(normalized_mobile_number))

    def _create_and_send_otp(self, user):
        chat_id = self._get_user_telegram_chat_id(user)
        if not chat_id:
            raise ValidationError("Telegram account is not linked for this user.")
        use_debug_preview = not settings.TELEGRAM_BOT_TOKEN and (
            settings.DEBUG or getattr(settings, "ALLOW_LOCAL_OTP_PREVIEW", False)
        )

        latest = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        if latest and not use_debug_preview and timezone.now() < latest.resend_available_at:
            seconds_left = int((latest.resend_available_at - timezone.now()).total_seconds())
            raise ValidationError(f"OTP resend is on cooldown for {seconds_left} more seconds.")

        self._check_request_limit(user)
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

        code = OTPService.generate_code()
        otp = PasswordResetOTP.objects.create(
            user=user,
            otp_hash=OTPService.hash_code(code),
            expires_at=OTPService.get_expiry(),
            resend_available_at=timezone.now() + timedelta(seconds=settings.TELEGRAM_OTP_RESEND_COOLDOWN_SECONDS),
        )
        minutes = max(1, settings.TELEGRAM_OTP_EXPIRY_SECONDS // 60)
        if not settings.TELEGRAM_BOT_TOKEN:
            if use_debug_preview:
                self._register_request_attempt(user)
                return otp, {
                    "message": "Telegram bot is not configured. Using local development OTP preview instead.",
                    "delivery_method": "debug_preview",
                    "otp_preview": code,
                    "otp_required": True,
                }
            raise ValidationError("Telegram OTP service is not configured. Add TELEGRAM_BOT_TOKEN in the backend environment.")
        try:
            self.telegram_service.send_otp(chat_id, f"Your OTP is {code}. Valid for {minutes} minute(s). Do not share it with anyone.")
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        except RequestException as exc:
            raise ValidationError("Unable to send OTP through Telegram right now. Please try again in a moment.") from exc
        self._register_request_attempt(user)
        return otp, {
            "message": "OTP sent to your Telegram app.",
            "delivery_method": "telegram",
            "otp_required": True,
        }

    def _verify_otp_record(self, user, otp: str) -> PasswordResetOTP:
        record = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        if not record:
            raise ValidationError("OTP was not requested.")
        if record.is_expired():
            record.is_used = True
            record.save(update_fields=["is_used"])
            raise ValidationError("OTP has expired.")
        if record.failed_attempts >= settings.PASSWORD_RESET_OTP_MAX_ATTEMPTS:
            record.is_used = True
            record.save(update_fields=["is_used"])
            raise ValidationError("OTP attempt limit reached. Please request a new OTP.")
        if record.otp_hash != OTPService.hash_code(otp):
            record.failed_attempts += 1
            updates = ["failed_attempts"]
            if record.failed_attempts >= settings.PASSWORD_RESET_OTP_MAX_ATTEMPTS:
                record.is_used = True
                updates.append("is_used")
            record.save(update_fields=updates)
            raise ValidationError("Invalid OTP.")
        record.is_verified = True
        record.is_used = True
        record.verified_at = timezone.now()
        record.save(update_fields=["is_verified", "is_used", "verified_at"])
        return record

    def _find_user_by_mobile(self, mobile_number: str):
        normalized_mobile_number = self._normalize_mobile_number(mobile_number)
        user = User.objects.filter(
            Q(phone_number__iexact=normalized_mobile_number) | Q(profile__mobile_number__iexact=normalized_mobile_number)
        ).first()
        if not user:
            raise ValidationError("User not found for this mobile number.")
        return user

    def _normalize_mobile_number(self, mobile_number: str) -> str:
        normalized_mobile_number = "".join(ch for ch in str(mobile_number or "") if ch.isdigit())
        if len(normalized_mobile_number) < 10:
            raise ValidationError("Enter a valid mobile number.")
        return normalized_mobile_number

    def _request_limit_key(self, user_id: int) -> str:
        return f"password-reset:requests:{user_id}"

    def _reset_token_key(self, token: str) -> str:
        return f"password-reset:token:{token}"

    def _otp_verified_key(self, mobile_number: str) -> str:
        return f"password-reset:verified:{mobile_number}"

    def _check_request_limit(self, user) -> None:
        attempts = int(cache.get(self._request_limit_key(user.pk), 0) or 0)
        if attempts >= settings.PASSWORD_RESET_OTP_REQUEST_LIMIT_PER_HOUR:
            raise ValidationError("OTP request limit reached. Please try again later.")

    def _register_request_attempt(self, user) -> None:
        key = self._request_limit_key(user.pk)
        attempts = int(cache.get(key, 0) or 0) + 1
        cache.set(key, attempts, self.REQUEST_LIMIT_WINDOW_SECONDS)

    def _find_user(self, identifier: str):
        raw_identifier = (identifier or "").strip()
        normalized_telegram_username = raw_identifier.lstrip("@")
        normalized_mobile_number = "".join(ch for ch in raw_identifier if ch.isdigit())
        user = User.objects.filter(
            Q(username__iexact=raw_identifier)
            | Q(email__iexact=raw_identifier)
            | Q(profile__telegram_username__iexact=raw_identifier)
            | Q(profile__telegram_username__iexact=normalized_telegram_username)
            | Q(phone_number__iexact=raw_identifier)
            | Q(phone_number__iexact=normalized_mobile_number)
            | Q(profile__mobile_number__iexact=raw_identifier)
            | Q(profile__mobile_number__iexact=normalized_mobile_number)
        ).first()
        if not user:
            raise ValidationError("User not found.")
        return user

    def _get_user_phone_number(self, user) -> str:
        return "".join(ch for ch in str(user.phone_number or user.profile.mobile_number or "") if ch.isdigit())

    def _get_user_telegram_chat_id(self, user) -> str:
        if user.telegram_chat_id is not None:
            return str(user.telegram_chat_id)
        return str(user.profile.telegram_chat_id or "").strip()
