from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
        ]


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
        ]

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Username is already in use.")
        return value

    def validate_email(self, value):
        user = self.instance
        normalized = value.strip()
        if User.objects.exclude(pk=user.pk).filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("Email is already in use.")
        return normalized


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        """
        Check that the new password and confirm password match.
        """
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                "New password and confirm password do not match."
            )
        return data
