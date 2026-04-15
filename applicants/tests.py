from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.test.utils import override_settings
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
import os

from departments.models import Department
from job_types.models import JobType
from jobs.models import Job
from applicants.models import Applicant
from applicants.services import send_applicant_status_notification
from notifications.models import EmailNotification


class PublicApplicantCreateTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.department = Department.objects.create(name="IT")
        self.job_type = JobType.objects.create(name="Full-time", code="FT")
        self.job = Job.objects.create(
            name="Backend Developer",
            department=self.department,
            job_type=self.job_type,
            is_active=True,
        )

    def test_public_create_ignores_status_field(self):
        url = reverse("add_applicant")
        payload = {
            "full_name": "Test Person",
            "email": "test@example.com",
            "contact_number": "09123456789",
            "job": self.job.id,
            "status": "hired",
        }
        resp = self.client.post(url, payload, format="json")

        self.assertEqual(resp.status_code, 201)

        applicant = Applicant.objects.get(email__iexact="test@example.com", job=self.job)
        self.assertEqual(applicant.status, "pending")
        self.assertEqual(EmailNotification.objects.count(), 1)
        notification = EmailNotification.objects.get(recipient="test@example.com")
        self.assertIn("Position Applied For: Backend Developer", notification.body)
        self.assertIn("Current Application Status: Pending", notification.body)
        self.assertIn("Kindly note that this verification link will expire in 24 hours.", notification.body)

    def test_public_create_resend_within_cooldown_is_blocked(self):
        url = reverse("add_applicant")
        payload = {
            "full_name": "Test Person",
            "email": "resend1@example.com",
            "contact_number": "09123456789",
            "job": self.job.id,
        }

        first = self.client.post(url, payload, format="json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(EmailNotification.objects.count(), 1)

        second = self.client.post(url, payload, format="json")
        self.assertEqual(second.status_code, 400)
        self.assertEqual(EmailNotification.objects.count(), 1)  # no new email queued

    def test_public_create_resend_after_cooldown_rotates_token(self):
        url = reverse("add_applicant")
        payload = {
            "full_name": "Test Person",
            "email": "resend2@example.com",
            "contact_number": "09123456789",
            "job": self.job.id,
        }

        first = self.client.post(url, payload, format="json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(EmailNotification.objects.count(), 1)

        applicant = Applicant.objects.get(email__iexact="resend2@example.com", job=self.job)
        old_token = applicant.verification_token
        self.assertIsNotNone(old_token)

        # Simulate old token so resend is allowed (cooldown is 15 min)
        applicant.token_created = timezone.now() - timedelta(minutes=16)
        applicant.save(update_fields=["token_created"])

        second = self.client.post(url, payload, format="json")
        self.assertEqual(second.status_code, 201)
        self.assertEqual(EmailNotification.objects.count(), 2)

        applicant.refresh_from_db()
        self.assertNotEqual(applicant.verification_token, old_token)
        self.assertTrue(applicant.token_created >= timezone.now() - timedelta(minutes=1))

    @override_settings(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    )
    def test_public_create_is_throttled(self):
        # Lower rate for this test so we can assert 429 deterministically
        rf = dict(settings.REST_FRAMEWORK)
        rf["DEFAULT_THROTTLE_RATES"] = {"public_applicant_submit": "1/min"}

        with override_settings(REST_FRAMEWORK=rf):
            url = reverse("add_applicant")

            payload = {
                "full_name": "AA",
                "email": "t1@example.com",
                "contact_number": "09123456789",
                "job": self.job.id,
            }

            r1 = self.client.post(url, payload, format="json")
            self.assertEqual(r1.status_code, 201)
            r2 = self.client.post(url, payload, format="json")
            self.assertEqual(r2.status_code, 429)

    @patch.dict(os.environ, {"CAPTCHA_SECRET_KEY": "dummy-secret"}, clear=False)
    def test_public_create_requires_captcha_when_configured(self):
        url = reverse("add_applicant")
        payload = {
            "full_name": "No Captcha",
            "email": "nocaptcha@example.com",
            "contact_number": "09123456789",
            "job": self.job.id,
        }

        resp = self.client.post(url, payload, format="json")

        self.assertEqual(resp.status_code, 400)

    def test_public_create_rejects_invalid_email(self):
        url = reverse("add_applicant")
        payload = {
            "full_name": "Test Person",
            "email": "not-an-email",
            "contact_number": "09123456789",
            "job": self.job.id,
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_public_create_rejects_invalid_contact_number(self):
        url = reverse("add_applicant")
        payload = {
            "full_name": "Test Person",
            "email": "valid@example.com",
            "contact_number": "abc123",
            "job": self.job.id,
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_public_create_trims_full_name(self):
        url = reverse("add_applicant")
        payload = {
            "full_name": "  Trim Me  ",
            "email": "trim@example.com",
            "contact_number": "09123456789",
            "job": self.job.id,
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        applicant = Applicant.objects.get(email__iexact="trim@example.com", job=self.job)
        self.assertEqual(applicant.full_name, "Trim Me")

    @patch.dict(os.environ, {"APPLICANT_UPLOAD_MAX_MB": "1"}, clear=False)
    def test_public_create_rejects_large_resume(self):
        url = reverse("add_applicant")
        big_pdf = SimpleUploadedFile(
            "resume.pdf",
            b"0" * (1024 * 1024 + 1),  # just over 1MB
            content_type="application/pdf",
        )
        payload = {
            "full_name": "Test Person",
            "email": "bigfile@example.com",
            "contact_number": "09123456789",
            "job": self.job.id,
            "resume": big_pdf,
        }
        resp = self.client.post(url, payload, format="multipart")
        self.assertEqual(resp.status_code, 400)


class ApplicantVerifyRedirectTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.department = Department.objects.create(name="IT")
        self.job_type = JobType.objects.create(name="Full-time", code="FT")
        self.job = Job.objects.create(
            name="Backend Developer",
            department=self.department,
            job_type=self.job_type,
            is_active=True,
        )

    @patch.dict(
        os.environ,
        {
            "APPLICANT_PORTAL_VERIFY_SUCCESS_URL": "https://applicant.example/success",
            "APPLICANT_PORTAL_VERIFY_EXPIRED_URL": "https://applicant.example/expired",
            "APPLICANT_PORTAL_VERIFY_INVALID_URL": "https://applicant.example/invalid",
        },
        clear=False,
    )
    def test_verify_success_redirects_and_updates_status(self):
        applicant = Applicant.objects.create(
            full_name="Verify Me",
            email="verify1@example.com",
            contact_number="09123456789",
            job=self.job,
            status="pending",
            verification_token="token-success",
            token_created=timezone.now(),
        )

        url = reverse("verify_applicant", kwargs={"token": "token-success"})
        resp = self.client.get(url, follow=False)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "https://applicant.example/success")

        applicant.refresh_from_db()
        self.assertEqual(applicant.status, "applied")
        self.assertIsNone(applicant.verification_token)
        self.assertEqual(EmailNotification.objects.count(), 2)
        self.assertEqual(
            EmailNotification.objects.filter(recipient="verify1@example.com").count(), 1
        )
        self.assertEqual(
            EmailNotification.objects.filter(recipient=os.environ.get("EMAIL_HOST_USER")).count(),
            1,
        )

        hr_notification = EmailNotification.objects.get(
            recipient=os.environ.get("EMAIL_HOST_USER")
        )
        self.assertIn("Position Applied For: Backend Developer", hr_notification.body)
        self.assertIn("Application Status: Applied", hr_notification.body)
        self.assertIn("Applicant Name: Verify Me", hr_notification.body)
        self.assertIn("Email Address: verify1@example.com", hr_notification.body)
        self.assertIn("Contact Number: 09123456789", hr_notification.body)

    @patch.dict(
        os.environ,
        {
            "APPLICANT_PORTAL_VERIFY_SUCCESS_URL": "https://applicant.example/success",
            "APPLICANT_PORTAL_VERIFY_EXPIRED_URL": "https://applicant.example/expired",
            "APPLICANT_PORTAL_VERIFY_INVALID_URL": "https://applicant.example/invalid",
        },
        clear=False,
    )
    def test_verify_expired_redirects(self):
        Applicant.objects.create(
            full_name="Expired",
            email="verify2@example.com",
            contact_number="09123456789",
            job=self.job,
            status="pending",
            verification_token="token-expired",
            token_created=timezone.now() - timedelta(days=2),
        )

        url = reverse("verify_applicant", kwargs={"token": "token-expired"})
        resp = self.client.get(url, follow=False)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "https://applicant.example/expired")

    @patch.dict(
        os.environ,
        {
            "APPLICANT_PORTAL_VERIFY_SUCCESS_URL": "https://applicant.example/success",
            "APPLICANT_PORTAL_VERIFY_EXPIRED_URL": "https://applicant.example/expired",
            "APPLICANT_PORTAL_VERIFY_INVALID_URL": "https://applicant.example/invalid",
        },
        clear=False,
    )
    def test_verify_invalid_redirects(self):
        url = reverse("verify_applicant", kwargs={"token": "does-not-exist"})
        resp = self.client.get(url, follow=False)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "https://applicant.example/invalid")


class ApplicantStatusEmailTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="IT")
        self.job_type = JobType.objects.create(name="Full-time", code="FT")
        self.job = Job.objects.create(
            name="Backend Developer",
            department=self.department,
            job_type=self.job_type,
            is_active=True,
        )
        self.applicant = Applicant.objects.create(
            full_name="Jane Applicant",
            email="jane@example.com",
            contact_number="09123456789",
            job=self.job,
            status="shortlisted",
        )

    def test_template_status_email_includes_job_application_summary(self):
        send_applicant_status_notification(self.applicant.id)

        notification = EmailNotification.objects.get(recipient=self.applicant.email)

        self.assertIn("Backend Developer", notification.body)
        self.assertIn("Position Applied For: Backend Developer", notification.body)
        self.assertIn("Current Application Status: Shortlisted", notification.body)
        self.assertIn(
            "We appreciate your continued interest in pursuing employment with ILPI.",
            notification.body,
        )

    def test_custom_status_email_formats_placeholders_and_appends_summary(self):
        send_applicant_status_notification(
            self.applicant.id,
            subject="Update Regarding Your {job_name} Application",
            body=(
                "Dear {applicant_full_name},\n\n"
                "We are pleased to inform you that your application remains under active review."
            ),
        )

        notification = EmailNotification.objects.get(recipient=self.applicant.email)

        self.assertEqual(
            notification.subject, "Update Regarding Your Backend Developer Application"
        )
        self.assertIn("Dear Jane Applicant,", notification.body)
        self.assertIn("Position Applied For: Backend Developer", notification.body)
        self.assertIn("Current Application Status: Shortlisted", notification.body)
