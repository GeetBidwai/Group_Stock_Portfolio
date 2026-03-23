from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.auth_module.models import PasswordResetOTP, UserSession
from apps.shared.services.otp_service import OTPService
from apps.shared.services.telegram_notification_service import TelegramNotificationService

User = get_user_model()


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
        if not user.profile.telegram_chat_id:
            raise ValidationError("Telegram account is not linked for this user.")
        latest = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        if latest and timezone.now() < latest.resend_available_at:
            seconds_left = int((latest.resend_available_at - timezone.now()).total_seconds())
            raise ValidationError(f"OTP resend is on cooldown for {seconds_left} more seconds.")

        code = OTPService.generate_code()
        otp = PasswordResetOTP.objects.create(
            user=user,
            otp_hash=OTPService.hash_code(code),
            expires_at=OTPService.get_expiry(),
            resend_available_at=timezone.now() + timedelta(seconds=settings.TELEGRAM_OTP_RESEND_COOLDOWN_SECONDS),
        )
        minutes = max(1, settings.TELEGRAM_OTP_EXPIRY_SECONDS // 60)
        self.telegram_service.send_otp(
            user.profile.telegram_chat_id,
            f"Your stock analytics reset code is {code}. It expires in {minutes} minute(s).",
        )
        return {"identifier": identifier, "expires_at": otp.expires_at, "otp_required": True}

    def verify_otp(self, identifier: str, otp: str) -> dict:
        if not settings.AUTH_RESET_REQUIRE_OTP:
            return {"verified": True, "otp_required": False}
        user = self._find_user(identifier)
        record = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        if not record:
            raise ValidationError("OTP was not requested.")
        if record.is_expired():
            raise ValidationError("OTP has expired.")
        if record.otp_hash != OTPService.hash_code(otp):
            raise ValidationError("Invalid OTP.")
        record.is_verified = True
        record.verified_at = timezone.now()
        record.save(update_fields=["is_verified", "verified_at"])
        return {"verified": True}

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

    def _find_user(self, identifier: str):
        user = User.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier) | Q(profile__telegram_username__iexact=identifier)
        ).first()
        if not user:
            raise ValidationError("User not found.")
        return user
