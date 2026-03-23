from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserSerializer


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    default_error_messages = {
        "email_not_found": "Incorrect email.",
        "username_not_found": "Incorrect username.",
        "incorrect_password": "Incorrect password.",
        "inactive_account": "This account is inactive.",
        "ambiguous_email": "Multiple accounts use this email. Log in with username.",
    }

    def validate(self, attrs):
        login = attrs["login"].strip()
        password = attrs["password"]
        is_email_login = "@" in login

        user = None
        if not is_email_login:
            user = User.objects.filter(username=login).first()

        if is_email_login:
            matches = User.objects.filter(Q(email__iexact=login))
            if matches.count() > 1:
                raise serializers.ValidationError(
                    {"login": [self.error_messages["ambiguous_email"]]}
                )
            user = matches.first()

        if not user:
            raise serializers.ValidationError(
                {
                    "login": [
                        self.error_messages[
                            "email_not_found" if is_email_login else "username_not_found"
                        ]
                    ]
                }
            )

        if not user.is_active:
            self.fail("inactive_account")

        authenticated_user = authenticate(
            request=self.context.get("request"),
            username=user.get_username(),
            password=password,
        )
        if not authenticated_user:
            raise serializers.ValidationError(
                {"password": [self.error_messages["incorrect_password"]]}
            )

        attrs["user"] = authenticated_user
        return attrs


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    user = UserSerializer()

    @classmethod
    def build_response(cls, user):
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
        }
