import hashlib
import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


class OTPService:
    @staticmethod
    def generate_code(length: int = 6) -> str:
        return "".join(str(random.randint(0, 9)) for _ in range(length))

    @staticmethod
    def hash_code(code: str) -> str:
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    @staticmethod
    def get_expiry():
        return timezone.now() + timedelta(seconds=settings.TELEGRAM_OTP_EXPIRY_SECONDS)
