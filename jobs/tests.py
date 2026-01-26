from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from departments.models import Department
from job_types.models import JobType
from jobs.models import Job


class PublicJobsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.department = Department.objects.create(name="IT")
        self.job_type = JobType.objects.create(name="Full-time", code="FT")

        today = timezone.localdate()

        # Should be included (active, no deadline)
        self.job_open = Job.objects.create(
            name="Backend Developer",
            department=self.department,
            job_type=self.job_type,
            job_description="Build APIs",
            requirements=["Django", "REST"],
            skills=["Python"],
            deadline=None,
            is_active=True,
        )

        # Should be excluded (deadline passed)
        self.job_expired = Job.objects.create(
            name="Old Role",
            department=self.department,
            job_type=self.job_type,
            deadline=today - timedelta(days=1),
            is_active=True,
        )

        # Should be excluded (inactive)
        self.job_inactive = Job.objects.create(
            name="Hidden Role",
            department=self.department,
            job_type=self.job_type,
            deadline=today + timedelta(days=30),
            is_active=False,
        )

    def test_public_jobs_list_no_auth_and_filters(self):
        url = reverse("public_job_list")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)

        # DRF default pagination may wrap results under "results"
        payload = resp.json()
        results = payload.get("results", payload)
        ids = {item["id"] for item in results}

        self.assertIn(self.job_open.id, ids)
        self.assertNotIn(self.job_expired.id, ids)
        self.assertNotIn(self.job_inactive.id, ids)
