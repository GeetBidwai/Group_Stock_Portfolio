from django.contrib.auth import authenticate, password_validation
from rest_framework import serializers

from apps.auth_module.models import TelegramLinkSession, User, UserProfile, UserSession


def normalize_phone_number(value):
    normalized_value = "".join(ch for ch in str(value or "") if ch.isdigit())
    return normalized_value


def normalize_telegram_chat_id(value):
    raw_value = str(value or "").strip()
    if not raw_value:
        return None
    if not raw_value.lstrip("-").isdigit():
        raise serializers.ValidationError("Enter a valid Telegram Chat ID.")
    return int(raw_value)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    telegram_chat_id = serializers.CharField(write_only=True, required=True, allow_blank=False)
    telegram_username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    mobile_number = serializers.CharField(write_only=True, required=True, allow_blank=False)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "telegram_chat_id",
            "telegram_username",
            "mobile_number",
            "phone_number",
        )

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_mobile_number(self, value):
        normalized_value = normalize_phone_number(value)
        if not normalized_value:
            raise serializers.ValidationError("Phone number is required.")
        if User.objects.filter(phone_number=normalized_value).exists() or UserProfile.objects.filter(mobile_number=normalized_value).exists():
            raise serializers.ValidationError("A user with this mobile number already exists.")
        return normalized_value

    def validate_phone_number(self, value):
        if not value:
            return ""
        return self.validate_mobile_number(value)

    def validate_telegram_chat_id(self, value):
        normalized_value = normalize_telegram_chat_id(value)
        if normalized_value is None:
            raise serializers.ValidationError("Telegram Chat ID is required.")
        if User.objects.filter(telegram_chat_id=normalized_value).exists():
            raise serializers.ValidationError("A user with this Telegram Chat ID already exists.")
        if UserProfile.objects.filter(telegram_chat_id=str(normalized_value)).exists():
            raise serializers.ValidationError("A user with this Telegram Chat ID already exists.")
        return normalized_value

    def create(self, validated_data):
        mobile_number = validated_data.pop("mobile_number", "") or validated_data.pop("phone_number", "")
        telegram_chat_id = validated_data.pop("telegram_chat_id", None)
        telegram_username = (validated_data.pop("telegram_username", "") or "").lstrip("@").strip()
        user = User.objects.create_user(**validated_data)
        user.phone_number = mobile_number or None
        user.telegram_chat_id = telegram_chat_id
        user.save(update_fields=["phone_number", "telegram_chat_id"])
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                "telegram_chat_id": str(telegram_chat_id or ""),
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
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "telegram_chat_id",
            "telegram_username",
            "mobile_number",
            "phone_number",
            "created_at",
        )

    def _get_profile(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return profile

    def get_telegram_chat_id(self, obj):
        return str(obj.telegram_chat_id) if obj.telegram_chat_id is not None else self._get_profile(obj).telegram_chat_id

    def get_telegram_username(self, obj):
        return self._get_profile(obj).telegram_username

    def get_mobile_number(self, obj):
        return obj.phone_number or self._get_profile(obj).mobile_number

    def get_phone_number(self, obj):
        return obj.phone_number or self._get_profile(obj).mobile_number


class ForgotPasswordRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()


class RequestResetOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=32, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=32, required=False, allow_blank=True)
    telegram_chat_id = serializers.CharField(max_length=32, required=False, allow_blank=True)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number") or attrs.get("mobile_number")
        normalized_phone = normalize_phone_number(phone_number)
        if not normalized_phone:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
        attrs["phone_number"] = normalized_phone

        raw_chat_id = attrs.get("telegram_chat_id", "")
        attrs["telegram_chat_id"] = normalize_telegram_chat_id(raw_chat_id) if raw_chat_id else None
        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    otp = serializers.CharField(min_length=6, max_length=6)


class VerifyResetOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=32, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=32, required=False, allow_blank=True)
    otp = serializers.CharField(min_length=6, max_length=6, required=False, allow_blank=True)
    otp_code = serializers.CharField(min_length=6, max_length=6, required=False, allow_blank=True)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number") or attrs.get("mobile_number")
        normalized_phone = normalize_phone_number(phone_number)
        if not normalized_phone:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})

        otp_code = (attrs.get("otp_code") or attrs.get("otp") or "").strip()
        if len(otp_code) != 6 or not otp_code.isdigit():
            raise serializers.ValidationError({"otp_code": "Enter a valid 6-digit OTP."})

        attrs["phone_number"] = normalized_phone
        attrs["otp_code"] = otp_code
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(min_length=8)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class ResetPasswordWithTokenSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=16, max_length=255, required=False, allow_blank=True)
    mobile_number = serializers.CharField(max_length=32, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=32, required=False, allow_blank=True)
    new_password = serializers.CharField(min_length=8, required=False, allow_blank=True)
    password = serializers.CharField(min_length=8, required=False, allow_blank=True)

    def validate(self, attrs):
        token = (attrs.get("token") or "").strip()
        phone_number = attrs.get("phone_number") or attrs.get("mobile_number")
        normalized_phone = normalize_phone_number(phone_number)
        new_password = attrs.get("new_password") or attrs.get("password") or ""

        if not token and not normalized_phone:
            raise serializers.ValidationError("Either reset token or phone number is required.")
        if len(new_password) < 8:
            raise serializers.ValidationError({"new_password": "Password must be at least 8 characters long."})
        password_validation.validate_password(new_password)

        attrs["token"] = token
        attrs["phone_number"] = normalized_phone
        attrs["new_password"] = new_password
        return attrs


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
