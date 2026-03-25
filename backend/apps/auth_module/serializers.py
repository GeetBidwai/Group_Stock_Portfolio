from django.contrib.auth import authenticate, password_validation
from rest_framework import serializers

from apps.auth_module.models import TelegramLinkSession, User, UserProfile, UserSession


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    telegram_chat_id = serializers.CharField(write_only=True, required=False, allow_blank=True)
    telegram_username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    mobile_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name", "telegram_chat_id", "telegram_username", "mobile_number")

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_mobile_number(self, value):
        normalized_value = "".join(ch for ch in str(value or "") if ch.isdigit())
        if normalized_value and UserProfile.objects.filter(mobile_number=normalized_value).exists():
            raise serializers.ValidationError("A user with this mobile number already exists.")
        return normalized_value

    def create(self, validated_data):
        telegram_chat_id = validated_data.pop("telegram_chat_id", "")
        telegram_username = (validated_data.pop("telegram_username", "") or "").lstrip("@").strip()
        mobile_number = "".join(ch for ch in str(validated_data.pop("mobile_number", "") or "") if ch.isdigit())
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                "telegram_chat_id": telegram_chat_id,
                "telegram_username": telegram_username,
                "mobile_number": mobile_number,
            },
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    telegram_chat_id = serializers.SerializerMethodField()
    telegram_username = serializers.SerializerMethodField()
    mobile_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "telegram_chat_id", "telegram_username", "mobile_number")

    def _get_profile(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return profile

    def get_telegram_chat_id(self, obj):
        return self._get_profile(obj).telegram_chat_id

    def get_telegram_username(self, obj):
        return self._get_profile(obj).telegram_username

    def get_mobile_number(self, obj):
        return self._get_profile(obj).mobile_number


class ForgotPasswordRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()


class RequestResetOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=32)


class VerifyOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    otp = serializers.CharField(min_length=6, max_length=6)


class VerifyResetOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=32)
    otp = serializers.CharField(min_length=6, max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(min_length=8)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class ResetPasswordWithTokenSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=16, max_length=255)
    new_password = serializers.CharField(min_length=8)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ("id", "user_agent", "ip_address", "is_active", "created_at", "last_seen_at")


class TelegramLinkSessionCreateSerializer(serializers.Serializer):
    pass


class TelegramLinkSessionStatusSerializer(serializers.ModelSerializer):
    linked = serializers.SerializerMethodField()
    expired = serializers.SerializerMethodField()

    class Meta:
        model = TelegramLinkSession
        fields = (
            "status",
            "linked",
            "expired",
            "telegram_username",
            "created_at",
            "expires_at",
        )

    def get_linked(self, obj):
        return obj.status == TelegramLinkSession.STATUS_LINKED

    def get_expired(self, obj):
        return obj.is_expired() or obj.status == TelegramLinkSession.STATUS_EXPIRED


class CompleteTelegramSignupSerializer(serializers.Serializer):
    session_token = serializers.CharField(min_length=16, max_length=128)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    mobile_number = serializers.CharField(max_length=32)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value
