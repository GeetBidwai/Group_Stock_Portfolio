import requests
from django.conf import settings


class TelegramNotificationService:
    def send_message(self, chat_id: str, message: str) -> None:
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")
        url = f"{settings.TELEGRAM_BOT_API_URL}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
        response.raise_for_status()

    def send_otp(self, chat_id: str, message: str) -> None:
        self.send_message(chat_id, message)
