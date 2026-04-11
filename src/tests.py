from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123"
        self.user = User.objects.create_user(
            username="hradmin",
            email="hradmin@example.com",
            password=self.password,
            first_name="HR",
            last_name="Admin",
            is_staff=True,
        )

    def test_login_with_username_sets_refresh_cookie(self):
        response = self.client.post(
            reverse("auth_login"),
            {"login": self.user.username, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)
        self.assertNotIn("refresh", response.data)
        self.assertIn(settings.AUTH_COOKIE_REFRESH_NAME, response.cookies)

    def test_login_with_email_sets_refresh_cookie(self):
        response = self.client.post(
            reverse("auth_login"),
            {"login": self.user.email, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_refresh_uses_cookie_and_returns_access(self):
        login_response = self.client.post(
            reverse("auth_login"),
            {"login": self.user.email, "password": self.password},
            format="json",
        )
        refresh_cookie = login_response.cookies[settings.AUTH_COOKIE_REFRESH_NAME].value
        self.client.cookies[settings.AUTH_COOKIE_REFRESH_NAME] = refresh_cookie

        response = self.client.post(reverse("auth_refresh"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn(settings.AUTH_COOKIE_REFRESH_NAME, response.cookies)

    def test_logout_clears_refresh_cookie(self):
        login_response = self.client.post(
            reverse("auth_login"),
            {"login": self.user.username, "password": self.password},
            format="json",
        )
        refresh_cookie = login_response.cookies[settings.AUTH_COOKIE_REFRESH_NAME].value
        self.client.cookies[settings.AUTH_COOKIE_REFRESH_NAME] = refresh_cookie

        response = self.client.post(reverse("auth_logout"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies[settings.AUTH_COOKIE_REFRESH_NAME].value, "")

    def test_me_returns_authenticated_user(self):
        login_response = self.client.post(
            reverse("auth_login"),
            {"login": self.user.username, "password": self.password},
            format="json",
        )
        access = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.get(reverse("auth_me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)

    def test_refresh_requires_cookie(self):
        response = self.client.post(reverse("auth_refresh"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_returns_username_not_found_for_unknown_username(self):
        response = self.client.post(
            reverse("auth_login"),
            {"login": "missing-user", "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["errors"]["login"][0], "Incorrect username."
        )

    def test_login_returns_email_not_found_for_unknown_email(self):
        response = self.client.post(
            reverse("auth_login"),
            {"login": "missing@example.com", "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["errors"]["login"][0], "Incorrect email."
        )

    def test_login_returns_incorrect_password_for_existing_user(self):
        response = self.client.post(
            reverse("auth_login"),
            {"login": self.user.username, "password": "WrongPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["errors"]["password"][0], "Incorrect password."
        )
