from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from requests import RequestException

from apps.shared.services.telegram_notification_service import TelegramNotificationService

User = get_user_model()


class Command(BaseCommand):
    help = "Validate Telegram OTP configuration and optionally inspect a user's phone/chat mapping."

    def add_arguments(self, parser):
        parser.add_argument("--phone-number", help="Phone number to inspect against the deployed database.")
        parser.add_argument("--telegram-chat-id", help="Optional expected Telegram chat ID for the user.")

    def handle(self, *args, **options):
        service = TelegramNotificationService()
        phone_number = self._normalize_digits(options.get("phone_number"))
        expected_chat_id = self._normalize_chat_id(options.get("telegram_chat_id"))

        self.stdout.write(f"DEBUG={settings.DEBUG}")
        self.stdout.write(f"AUTH_RESET_REQUIRE_OTP={settings.AUTH_RESET_REQUIRE_OTP}")
        self.stdout.write(f"TELEGRAM_BOT_API_URL={settings.TELEGRAM_BOT_API_URL}")
        self.stdout.write(f"TELEGRAM_BOT_TOKEN_SET={bool(settings.TELEGRAM_BOT_TOKEN)}")

        try:
            bot_payload = service.get_me()
            bot_result = bot_payload.get("result") or {}
            self.stdout.write(
                self.style.SUCCESS(
                    f"Telegram bot reachable: @{bot_result.get('username', 'unknown')} ({bot_result.get('id', 'n/a')})"
                )
            )
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        except RequestException as exc:
            raise CommandError(f"Telegram API is unreachable from this environment: {exc}") from exc

        if not phone_number:
            return

        user = (
            User.objects.select_related("profile")
            .filter(phone_number__iexact=phone_number)
            .first()
            or User.objects.select_related("profile").filter(profile__mobile_number__iexact=phone_number).first()
        )
        if not user:
            raise CommandError(f"No user found for phone number {phone_number}.")

        stored_phone = self._normalize_digits(getattr(user, "phone_number", "") or getattr(user.profile, "mobile_number", ""))
        stored_chat_id = self._stored_chat_id(user)
        self.stdout.write(self.style.SUCCESS(f"User found: {user.username}"))
        self.stdout.write(f"Stored phone number: {stored_phone or '<empty>'}")
        self.stdout.write(f"Stored Telegram chat ID: {stored_chat_id or '<empty>'}")

        if expected_chat_id and stored_chat_id != expected_chat_id:
            raise CommandError(
                f"Telegram chat ID mismatch. Expected {expected_chat_id}, stored {stored_chat_id or '<empty>'}."
            )

    def _normalize_digits(self, value: str | None) -> str:
        return "".join(ch for ch in str(value or "") if ch.isdigit())

    def _normalize_chat_id(self, value: str | None) -> str:
        raw = str(value or "").strip()
        if not raw:
            return ""
        if not raw.lstrip("-").isdigit():
            raise CommandError("Telegram chat ID must be numeric.")
        return raw

    def _stored_chat_id(self, user) -> str:
        if getattr(user, "telegram_chat_id", None) is not None:
            return str(user.telegram_chat_id)
        return str(getattr(user.profile, "telegram_chat_id", "") or "").strip()
