from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Safely set a user's phone number and Telegram chat ID in both User and UserProfile."

    def add_arguments(self, parser):
        parser.add_argument("--username", help="Username of the user to update.")
        parser.add_argument("--email", help="Email of the user to update.")
        parser.add_argument("--phone-number", required=True, help="Phone number to store for the user.")
        parser.add_argument("--telegram-chat-id", required=True, help="Telegram chat ID to store for the user.")

    def handle(self, *args, **options):
        username = (options.get("username") or "").strip()
        email = (options.get("email") or "").strip()
        phone_number = self._normalize_phone_number(options["phone_number"])
        telegram_chat_id = self._normalize_chat_id(options["telegram_chat_id"])

        if not username and not email:
            raise CommandError("Provide --username or --email to identify the user.")

        user = self._get_user(username=username, email=email)
        if user is None:
            raise CommandError("User not found.")

        conflict = (
            User.objects.exclude(pk=user.pk)
            .filter(phone_number=phone_number)
            .values_list("username", flat=True)
            .first()
        )
        if conflict:
            raise CommandError(f"Phone number {phone_number} is already assigned to user {conflict}.")

        user.phone_number = phone_number
        user.telegram_chat_id = int(telegram_chat_id)
        user.save(update_fields=["phone_number", "telegram_chat_id"])

        profile, _ = user.profile.__class__.objects.get_or_create(user=user)
        profile.mobile_number = phone_number
        profile.telegram_chat_id = telegram_chat_id
        profile.save(update_fields=["mobile_number", "telegram_chat_id"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {user.username}: phone_number={user.phone_number}, telegram_chat_id={user.telegram_chat_id}"
            )
        )

    def _get_user(self, username: str, email: str):
        if username:
            user = User.objects.filter(username__iexact=username).first()
            if user:
                return user
        if email:
            user = User.objects.filter(email__iexact=email).first()
            if user:
                return user
        return None

    def _normalize_phone_number(self, value: str) -> str:
        normalized = "".join(ch for ch in str(value or "") if ch.isdigit())
        if len(normalized) < 10:
            raise CommandError("Enter a valid phone number.")
        return normalized

    def _normalize_chat_id(self, value: str) -> str:
        raw = str(value or "").strip()
        if not raw.lstrip("-").isdigit():
            raise CommandError("Enter a valid Telegram chat ID.")
        return raw
