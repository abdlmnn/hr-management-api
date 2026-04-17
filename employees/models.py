from django.db import models

from applicants.models import Applicant
from job_types.models import JobType
from jobs.models import Job
from jobs.utils import now


class Employee(models.Model):
    class Meta:
        ordering = ["-id"]
        db_table = "employees"
        verbose_name_plural = "Employees"

    applicant = models.OneToOneField(
        Applicant,
        on_delete=models.CASCADE,
        related_name="employee",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employees",
    )
    employment_type = models.ForeignKey(
        JobType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employees",
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )
    date_started = models.DateField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_by = models.CharField(
        max_length=10,
        default="sys",
        null=True,
        blank=True,
    )
    updated_by = models.CharField(
        max_length=10,
        default="sys",
        null=True,
        blank=True,
    )
    date_created = models.DateTimeField(
        default=now,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.employee_id or f"Employee {self.pk}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        update_fields = kwargs.get("update_fields")
        super().save(*args, **kwargs)

        if (is_new or not self.employee_id) and self.pk:
            self.employee_id = f"EMP-{self.pk:06d}"
            if update_fields is not None:
                update_fields = set(update_fields)
                update_fields.add("employee_id")
                kwargs["update_fields"] = list(update_fields)
            super().save(update_fields=["employee_id"])
