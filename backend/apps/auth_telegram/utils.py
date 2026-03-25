from __future__ import annotations

from hashlib import sha256
import hmac

from django.conf import settings


def verify_telegram_auth(data: dict) -> bool:
    payload = dict(data or {})
    received_hash = payload.pop("hash", None)
    auth_date = payload.get("auth_date")
    if not received_hash or not auth_date:
        return False

    try:
        auth_timestamp = int(auth_date)
    except (TypeError, ValueError):
        return False

    max_age = int(getattr(settings, "TELEGRAM_AUTH_MAX_AGE_SECONDS", 86400))
    from time import time
    if auth_timestamp < int(time()) - max_age:
        return False

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(payload.items())
        if value not in (None, "")
    )
    secret_key = sha256(settings.TELEGRAM_BOT_TOKEN.encode("utf-8")).digest()
    computed_hash = hmac.new(
        secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=sha256,
    ).hexdigest()
    return hmac.compare_digest(computed_hash, received_hash)
