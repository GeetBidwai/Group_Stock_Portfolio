from django.conf import settings


def is_enabled(flag_name: str) -> bool:
    return settings.FEATURE_FLAGS.get(flag_name, False)
