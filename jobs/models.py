from django.db import models
from .utils import now
from departments.models import Department
from job_types.models import JobType


class Job(models.Model):
    class Meta:
        ordering = ["-id"]
        db_table = "jobs"
        verbose_name_plural = "Jobs"

    def __str__(self):
        return f"{self.name}"

    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="jobs",
    )
    job_type = models.ForeignKey(
        JobType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="jobs",
    )
    job_description = models.TextField(
        blank=True,
        null=True,
    )
    requirements = models.TextField(
        blank=True,
        null=True,
    )
    deadline = models.DateField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
    )
    created_by = models.CharField(
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
