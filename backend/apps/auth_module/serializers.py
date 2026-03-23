from django.contrib.auth import authenticate, password_validation
from rest_framework import serializers

from apps.auth_module.models import User, UserProfile, UserSession


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    telegram_chat_id = serializers.CharField(write_only=True, required=False, allow_blank=True)
    telegram_username = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name", "telegram_chat_id", "telegram_username")

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        telegram_chat_id = validated_data.pop("telegram_chat_id", "")
        telegram_username = validated_data.pop("telegram_username", "")
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.filter(user=user).update(
            telegram_chat_id=telegram_chat_id,
            telegram_username=telegram_username,
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
    telegram_chat_id = serializers.CharField(source="profile.telegram_chat_id", read_only=True)
    telegram_username = serializers.CharField(source="profile.telegram_username", read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "telegram_chat_id", "telegram_username")


class ForgotPasswordRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()


class VerifyOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    otp = serializers.CharField(min_length=6, max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(min_length=8)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ("id", "user_agent", "ip_address", "is_active", "created_at", "last_seen_at")
