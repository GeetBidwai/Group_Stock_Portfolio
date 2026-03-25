from rest_framework import serializers


class TelegramAuthSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    username = serializers.CharField(max_length=255, required=False, allow_blank=True)
    photo_url = serializers.URLField(required=False, allow_blank=True)
    auth_date = serializers.CharField(max_length=32)
    hash = serializers.CharField(max_length=128)


class SetMPINSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField(min_value=1)
    mpin = serializers.RegexField(regex=r"^\d{4}$")


class LoginMPINSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField(min_value=1)
    mpin = serializers.RegexField(regex=r"^\d{4}$")


class MobileOTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=32)


class MobileOTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=32)
    otp = serializers.CharField(min_length=6, max_length=6)


class ResetMPINSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField(min_value=1)
    new_mpin = serializers.RegexField(regex=r"^\d{4}$")
