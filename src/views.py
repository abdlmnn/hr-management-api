from django.conf import settings
from django.contrib.auth.models import update_last_login
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserSerializer

from .serializers import LoginResponseSerializer, LoginSerializer


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        settings.AUTH_COOKIE_REFRESH_NAME,
        refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_COOKIE_PATH,
        domain=settings.AUTH_COOKIE_DOMAIN,
    )


def clear_refresh_cookie(response):
    response.delete_cookie(
        settings.AUTH_COOKIE_REFRESH_NAME,
        path=settings.AUTH_COOKIE_PATH,
        domain=settings.AUTH_COOKIE_DOMAIN,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        update_last_login(None, user)
        payload = LoginResponseSerializer.build_response(user)
        refresh_token = payload.pop("refresh")

        response = Response(payload, status=status.HTTP_200_OK)
        set_refresh_cookie(response, refresh_token)
        return response


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_refresh"

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH_NAME)
        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0])

        response = Response(
            {"access": serializer.validated_data["access"]},
            status=status.HTTP_200_OK,
        )

        rotated_refresh = serializer.validated_data.get("refresh")
        if rotated_refresh:
            set_refresh_cookie(response, rotated_refresh)
        return response


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_logout"

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH_NAME)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        response = Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )
        clear_refresh_cookie(response)
        return response


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
