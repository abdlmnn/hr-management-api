from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from applicants.models import Applicant
from departments.models import Department
from employees.models import Employee
from job_types.models import JobType
from jobs.models import Job


class EmployeeProvisioningTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="IT")
        self.job_type = JobType.objects.create(name="Full-Time", code="FT")
        self.job = Job.objects.create(
            name="Backend Developer",
            department=self.department,
            job_type=self.job_type,
            is_active=True,
        )

    def test_hired_applicant_creates_employee(self):
        applicant = Applicant.objects.create(
            full_name="Jane Applicant",
            email="jane@example.com",
            contact_number="09123456789",
            job=self.job,
            status="applied",
        )

        applicant.status = "hired"
        applicant.save(update_fields=["status"])

        employee = Employee.objects.get(applicant=applicant)
        self.assertEqual(employee.job, self.job)
        self.assertEqual(employee.employment_type, self.job_type)
        self.assertTrue(employee.employee_id.startswith("EMP-"))

    def test_repeated_hired_status_does_not_duplicate_employee(self):
        applicant = Applicant.objects.create(
            full_name="John Applicant",
            email="john@example.com",
            contact_number="09123456789",
            job=self.job,
            status="hired",
        )

        applicant.save()
        applicant.updated_by = "admin"
        applicant.save(update_fields=["updated_by"])

        self.assertEqual(Employee.objects.filter(applicant=applicant).count(), 1)


class EmployeeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="tester", password="secret123")
        self.client.force_authenticate(self.user)

        self.department = Department.objects.create(name="IT")
        self.other_department = Department.objects.create(name="HR")
        self.job_type = JobType.objects.create(name="Full-Time", code="FT")
        self.other_job_type = JobType.objects.create(name="Contract", code="CT")
        self.job = Job.objects.create(
            name="Backend Developer",
            department=self.department,
            job_type=self.job_type,
            is_active=True,
        )
        self.other_job = Job.objects.create(
            name="HR Coordinator",
            department=self.other_department,
            job_type=self.other_job_type,
            is_active=True,
        )
        self.applicant = Applicant.objects.create(
            full_name="Jamie Employee",
            email="jamie@example.com",
            contact_number="09123456789",
            job=self.job,
            status="hired",
        )
        self.employee = Employee.objects.get(applicant=self.applicant)

    def test_employee_list_returns_hired_employee_data(self):
        response = self.client.get(reverse("employee_list"))

        self.assertEqual(response.status_code, 200)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["employment_type_name"], "Full-Time")
        self.assertEqual(results[0]["job_name"], "Backend Developer")

    def test_employee_update_persists_employee_and_applicant_fields(self):
        response = self.client.patch(
            reverse("update_employee", kwargs={"id": self.employee.id}),
            {
                "full_name": "Jamie Updated",
                "email": "updated@example.com",
                "contact_number": "09999999999",
                "status": "hired",
                "job": self.other_job.id,
                "employment_type": self.other_job_type.id,
                "date_started": "2026-04-17",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.employee.refresh_from_db()
        self.applicant.refresh_from_db()

        self.assertEqual(self.employee.job, self.other_job)
        self.assertEqual(self.employee.employment_type, self.other_job_type)
        self.assertEqual(str(self.employee.date_started), "2026-04-17")
        self.assertEqual(self.applicant.full_name, "Jamie Updated")
        self.assertEqual(self.applicant.email, "updated@example.com")
        self.assertEqual(self.applicant.contact_number, "09999999999")

    def test_employee_list_can_filter_by_department(self):
        response = self.client.get(f"{reverse('employee_list')}?department={self.department.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get("results", [])), 1)

        response = self.client.get(f"{reverse('employee_list')}?department={self.other_department.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get("results", [])), 0)
