from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.auth_module.models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=UserProfile)
def sync_profile_fields_to_user(sender, instance, **kwargs):
    normalized_phone = "".join(ch for ch in str(instance.mobile_number or "") if ch.isdigit()) or None
    normalized_chat_id = None
    raw_chat_id = str(instance.telegram_chat_id or "").strip()
    if raw_chat_id.lstrip("-").isdigit():
        normalized_chat_id = int(raw_chat_id)

    User.objects.filter(pk=instance.user_id).update(
        phone_number=normalized_phone,
        telegram_chat_id=normalized_chat_id,
    )
