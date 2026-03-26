from django.contrib.auth import authenticate, password_validation
from rest_framework import serializers

from apps.auth_module.models import User, UserProfile, UserSession


def normalize_phone_number(value):
    return "".join(ch for ch in str(value or "") if ch.isdigit())


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    mobile_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "mobile_number",
            "phone_number",
        )

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_mobile_number(self, value):
        normalized_value = normalize_phone_number(value)
        if not normalized_value:
            return ""
        if User.objects.filter(phone_number=normalized_value).exists() or UserProfile.objects.filter(mobile_number=normalized_value).exists():
            raise serializers.ValidationError("A user with this mobile number already exists.")
        return normalized_value

    def validate_phone_number(self, value):
        return self.validate_mobile_number(value)

    def create(self, validated_data):
        mobile_number = validated_data.pop("mobile_number", "") or validated_data.pop("phone_number", "")
        user = User.objects.create_user(**validated_data)
        if mobile_number:
            user.phone_number = mobile_number
            user.save(update_fields=["phone_number"])
        UserProfile.objects.update_or_create(
            user=user,
            defaults={"mobile_number": mobile_number},
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
            "mobile_number",
            "phone_number",
            "created_at",
        )

    def _get_profile(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return profile

    def get_mobile_number(self, obj):
        return obj.phone_number or self._get_profile(obj).mobile_number

    def get_phone_number(self, obj):
        return obj.phone_number or self._get_profile(obj).mobile_number


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ("id", "user_agent", "ip_address", "is_active", "created_at", "last_seen_at")
